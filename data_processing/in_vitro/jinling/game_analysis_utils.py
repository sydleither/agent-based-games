# --------------------------------------------------------------------
# Functions to help with analysing game assay data
# By: Maximilian Strobl, April 27 2025
# --------------------------------------------------------------------
import os
import shlex
import subprocess
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------------------------------------------
def run_cellprofiler_on_well(well_id, cellprofiler_path, pipeline_file, dir_to_analyse, output_dir, 
                             create_out_dir=True, var_name_well="Metadata_Well", 
                             print_command=False, log_level=50, suppress_output=True):
    '''
    Run cellprofiler on a single well
    log_level: Set the verbosity for logging messages: 10 or DEBUG
               for debugging, 20 or INFO for informational, 30 or
               WARNING for warning, 40 or ERROR for error, 50 or
               CRITICAL for critical, 50 or FATAL for fatal.
               Otherwise, the argument is interpreted as the file
               name of a log configuration file (see
               http://docs.python.org/library/logging.config.html for
               file format). Taken from cellprofiler docs.
    '''
    # Cellprofiler will save its output to the same file and that file name is not changeable.
    # Only workaround is to make it output into a dedicated directory.
    curr_out_dir = output_dir
    if create_out_dir:
        curr_out_dir = os.path.join(output_dir, well_id)
        if not os.path.exists(curr_out_dir):
            os.mkdir(curr_out_dir)
    command = "{} -c -r -p {} -i {} -o {} -g {}={} -L {}".format(
                                                           cellprofiler_path, 
                                                           pipeline_file, 
                                                           shlex.quote(dir_to_analyse), # Format the directory name to make it safe for the command line
                                                           shlex.quote(curr_out_dir), # Format the directory name to make it safe for the command line
                                                        #    dir_to_analyse.replace(" ", "\b"), # Format the directory name to make it safe for the command line
                                                        #    curr_out_dir.replace(" ", "\b"), # Format the directory name to make it safe for the command line
                                                           var_name_well, well_id, 
                                                           log_level)
    if print_command: print(command)
    # os.system(command)
    kws_dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL} if suppress_output else {}
    subprocess.run(command, shell=True, **kws_dict)

# ---------------------------------------------------------------------------------------------------------------
def load_cellprofiler_data(input_file, imaging_frequency=4, tags=['gfp', 'texasred'], pop_names=['S', 'R'], ignore_column=11, long_format=True):
    """
    Load cellprofiler data and return a pandas dataframe in either wide or long format (as requested)
    input_file: path to the cellprofiler output file to be loaded
    imaging_frequency: imaging frequency in hours
    tags: list of tags used in the cellprofiler output file (e.g. gfp and texasred)
    pop_names: list of population names (e.g. S and R)
    long_format: if True, return a long dataframe with columns: Time, WellId, CellType, Count
    """
    if type(input_file) == str: # Allow user to input file name or data frame directly
        counts_raw_df = pd.read_csv(input_file, index_col=False)
    else:
        counts_raw_df = input_file
    counts_raw_df['WellId'] = counts_raw_df['FileName_%s'%tags[0]].str.split('_').str[0]
    counts_raw_df['RowId'] = counts_raw_df['WellId'].str[0]
    counts_raw_df['ColumnId'] = counts_raw_df['WellId'].str[1:].astype(int)
    if ignore_column is not None:
        counts_raw_df = counts_raw_df[counts_raw_df['ColumnId'] != 11]
    counts_raw_df['ImageId'] = counts_raw_df['FileName_%s'%tags[0]].str.split('_').str[-1].str.split('.').str[0].astype(int)
    counts_raw_df['Time'] = (counts_raw_df['ImageId']-1) * imaging_frequency
    counts_raw_df['Count_total'] = counts_raw_df['Count_%s_objects'%tags[0]] + counts_raw_df['Count_%s_objects'%tags[1]]
    counts_raw_df['Frequency_%s_objects'%tags[0]] = counts_raw_df['Count_%s_objects'%tags[0]] / counts_raw_df['Count_total']
    counts_raw_df['Frequency_%s_objects'%tags[1]] = counts_raw_df['Count_%s_objects'%tags[1]] / counts_raw_df['Count_total']
    # Convert to long format if requested
    if long_format:
        tmp_list = []       
        for measure in ['Count', 'Frequency']:
            counts_raw_df_long = counts_raw_df.melt(id_vars=['Time', 'WellId', 'ImageId', 'RowId', 'ColumnId'], 
                                value_vars=['%s_%s_objects'%(measure, tags[0]), '%s_%s_objects'%(measure, tags[1])], 
                                var_name='CellType', value_name=measure)
            counts_raw_df_long.replace({'CellType': {'%s_%s_objects'%(measure, tags[0]): pop_names[0], 
                                                '%s_%s_objects'%(measure, tags[1]): pop_names[1]}},  
                                                inplace=True)
            counts_raw_df_long.reset_index(drop=True, inplace=True)
            tmp_list.append(counts_raw_df_long)
        counts_raw_df = pd.merge(tmp_list[0], tmp_list[1], on=['Time', 'WellId', 'ImageId', 'RowId', 'ColumnId', 'CellType'])
        counts_raw_df.reset_index(drop=True, inplace=True)
    return counts_raw_df

# ---------------------------------------------------------------------------------------------------------------
def map_well_to_experimental_condition(well_id, experimental_conditions_df):
    '''
    Retrieves the experimental condition for a well from the layout excel
    file in the structure used for the game pipeline.
    '''
    row_id = well_id[0].lower()
    column_id = int(well_id[1:])
    return experimental_conditions_df.loc[row_id, column_id]

# ---------------------------------------------------------------------------------------------------------------
def plot_data(dataDf, x="Time", y='Confluence', style=None, hue=None, estimator=None,
              err_style="bars", errorbar=('ci', 95), linecolor='black', linewidth=2, palette="tab10", legend=False,
              markerstyle='o', markersize=12, markeredgewidth=0.5, markeredgecolor='black', lineplot_kws={},
              plot_drug=True, treatment_column="DrugConcentration", treatment_notation_mode="post",
              drug_bar_position=0.85, drug_colour="#683073", 
              xlim=None, ylim=None, y2lim=1,
              title="", label_axes=False,
              ax=None, figsize=(10, 8), **kwargs):
    '''
    Plot longitudinal data (e.g. cell counts), together with annotations of drug administration.
    :param dataDf: Pandas data frame with longitudinal data to be plotted.
    :param x: Name (str) of the column with the time information.
    :param y: Name (str) of the column with the metric to be plotted on the y-axis (e.g. cell count, confluence, etc).
    :param style: Name (str) of the column with the style information (e.g. cell type).
    :param hue: Name (str) of the column with the hue information (e.g. drug treatment).
    :param estimator: Name (str) of the estimator to use for the line plot (e.g. mean, median).
    :param err_style: Name (str) of the error style to use for the line plot (e.g. bars, band).
    :param errorbar: Tuple with the type of error bar to plot and the confidence interval (e.g. ('ci', 95)).
    :param linecolor: Colour of the line plot.
    :param linewidth: Width of the line plot.
    :param palette: Colour palette to use for the line plot.
    :param legend: Boolean; whether or not to show the legend.
    :param markerstyle: Style of the markers for the data points.
    :param markersize: Size of the markers for the data points.
    :param markeredgewidth: Width of the marker edge.
    :param markeredgecolor: Colour of the marker edge.
    :param lineplot_kws: Dictionary with additional keyword arguments for the line plot.
    :param plot_drug: Boolean; whether or not to plot the treatment schedule.
    :param treatment_column: Name (str) of the column with the information about the dose administered.
    :param treatment_notation_mode: Name (str) of the mode to use for the treatment notation (e.g. post, pre).
    :param drug_bar_position: Position of the drug bar when plotted across the top.
    :param drug_colour: Colour of the drug bar.
    :param xlim: x-axis limit.
    :param ylim: y-axis limit.
    :param y2lim: y2-axis limit.
    :param title: Title to put on the figure.
    :param label_axes: Boolean; whether or not to label the axes.
    :param ax: matplotlib axis to plot on. If none provided creates a new figure.
    :param figsize: Tuple, figure dimensions when creating new figure.
    :param kwargs: Other kwargs to pass to plotting functions.
    :return:
    '''

    if ax is None: fig, ax = plt.subplots(1, 1, figsize=figsize)
    # Set a number of defaults that I like
    lineplot_kws['errorbar'] = errorbar
    lineplot_kws['estimator'] = estimator
    lineplot_kws['hue'] = hue
    lineplot_kws['style'] = style
    lineplot_kws['err_style'] = err_style
    lineplot_kws['linecolor'] = lineplot_kws.get('linecolor', linecolor)
    lineplot_kws['linewidth'] = linewidth
    lineplot_kws['palette'] = palette
    lineplot_kws['legend'] = legend
    if hue == None:
        lineplot_kws['color'] = lineplot_kws['linecolor']
        lineplot_kws.pop('palette')
    lineplot_kws.pop('linecolor', None)
    lineplot_kws['markerstyle'] = markerstyle
    lineplot_kws['markersize'] = markersize
    lineplot_kws['markeredgewidth'] = markeredgewidth
    lineplot_kws['markeredgecolor'] = markeredgecolor
    # Plot the data
    if lineplot_kws['style']==None: # If no style is specified, use the "marker" keyword. Otherwise points won't show up.
        lineplot_kws['marker'] = lineplot_kws['markerstyle']
    else:
        lineplot_kws['markers'] = lineplot_kws['markerstyle']
    lineplot_kws.pop('markerstyle')
    sns.lineplot(x=x, y=y, **lineplot_kws, ax=ax, data=dataDf)

    # Format the plot
    if xlim is not None: ax.set_xlim(0, xlim)
    if ylim is not None: ax.set_ylim(0, ylim)

    # Decorate the plot
    if label_axes == False:
        ax.set_xlabel("")
        ax.set_ylabel("")
    ax.set_title(title)
    ax.tick_params(labelsize=kwargs.get("labelsize", 28))
    plt.tight_layout()


# ---------------------------------------------------------------------------------------------------------------
def estimate_growth_rate(data_df, well_id=None, cell_type=None, growth_rate_window=[0, 24], count_threshold=10):
    """
    Estimate the (exponential) growth rate of a cell population in a well.
    data_df: pandas dataframe containing the cell count data
    well_id: well identifier; if not None, assume data is from a single well
    cell_type: cell type identifier; if not None, assume data is from a single cell type
    growth_rate_window: time window for estimating the growth rate
    Returns: growth rate, intercept, lower bound of the growth rate, upper bound of the growth rate
    """
    # Filter the data
    curr_df = data_df.copy()
    if well_id is not None:
        curr_df = curr_df[curr_df["WellId"] == well_id]
    if cell_type is not None:
        curr_df = curr_df[curr_df["CellType"] == cell_type]
    curr_df = curr_df[curr_df["Time"].between(growth_rate_window[0], growth_rate_window[1])]

    # Quality control data
    if curr_df["Count"].min() <= 0: # Check for negative values
        print("Zero or negative values detected in the count data. Skipping analysis of %s data for well %s." % (cell_type, well_id))
        return np.nan, np.nan, np.nan, np.nan
    elif curr_df["Count"].mean() < count_threshold: # Check for low counts
        print("Low counts detected in the count data. Skipping analysis of %s data for well %s." % (cell_type, well_id))
        return np.nan, np.nan, np.nan, np.nan
    
    # Fit a linear model to the log-transformed data. Use the theil-sen estimator
    x = curr_df["Time"].values - curr_df["Time"].values[0] # Start the time at 0
    y = np.log(curr_df["Count"].values) # Log-transform
    slope, intercept, low_slope, high_slope = stats.theilslopes(y, x)

    return slope, intercept, low_slope, high_slope

# ---------------------------------------------------------------------------------------------------------------
def compute_population_fraction(counts_df, fraction_window=None, n_images="all", well_id=None, cell_type_list=None):
    """
    Compute the fraction of a (or each) cell population in a well.
    counts_df: pandas dataframe containing the cell count data
    fraction_window: time window for computing the fraction
    n_images: number of images to include in the computation; if "all", include all images
    well_id: well identifier; if not None, assume data is from a single well
    cell_type_list: list of cell types to include in the computation; if None, include all cell types
    Returns: dictionary containing the fraction of each cell type
    """

    # Format the data
    cell_type_list = cell_type_list if cell_type_list is not None else counts_df["CellType"].unique()
    curr_df = counts_df.copy() # Make a copy to avoid modifying the original dataframe
    if well_id is not None: # Filter by well_id if requested
        curr_df = curr_df[(curr_df["WellId"] == well_id)]

    # Turn to wide format for easier manipulation
    curr_df = counts_df[(counts_df["WellId"] == well_id)].copy()
    curr_df = curr_df.pivot(index="Time", columns="CellType", values="Count")
    curr_df = curr_df.reset_index()
    curr_df["TotalCount"] = curr_df[cell_type_list].sum(axis=1)
    fraction_list = []
    for cell_type in cell_type_list:
        curr_df["Fraction_%s"%cell_type] = curr_df[cell_type] / curr_df["TotalCount"]
        fraction_list.append("Fraction_%s"%cell_type)

    # Return the fraction using the requested method
    if fraction_window == None:
        fraction_window = [curr_df["Time"].min(), curr_df["Time"].max()]
    curr_df = curr_df[curr_df["Time"].between(fraction_window[0], fraction_window[1])]
    if n_images != "all":
        if n_images >= 0:
            curr_df = curr_df.iloc[:n_images]
        else:
            curr_df = curr_df.iloc[n_images:]
    return curr_df[fraction_list].mean().to_dict()

# ---------------------------------------------------------------------------------------------------------------
def estimate_game_parameters(growth_rate_df, fraction_col="Fraction_Sensitive", growth_rate_col="GrowthRate", 
                             cell_type_col="CellType", cell_type_list=None, method="theil", ci=0.95):
    """
    Estimate the game parameters from the growth rate data. The game parameters are the pay-off matrix entries,
    where we assume that the pay-off matrix is of the form:
    P = |p11 p12|
        |p21 p22|
    where pij is the pay-off for cell type i when interacting with cell type j. Which of the two cell types is
    Type 1 and Type 2, respectively, is determined by the order of the cell_type_list.
    Parameters
    ----------
    growth_rate_df : the growth rate data
    fraction_col : the column name for the population fraction
    growth_rate_col : the column name for the growth rate
    cell_type_col : the column name for the cell type
    cell_type_list : the list of cell types; used to determine the order of the pay-off matrix entries. If None, the order is determined by the order of the cell types in the data.
    method : the method to use for the estimation. Can be "ols" or "theil".
    ci : the confidence interval for the Theil estimator
    Returns
    -------
    params_dict : a dictionary with the pay-off matrix entries and the advantage of each cell type (game space position).
    """
    # Check input
    supported_methods_list = ["ols", "theil"]
    if method not in supported_methods_list:
        raise ValueError("Method must be one of %s"%supported_methods_list)
    
    # Estimate the game parameters
    coeffs_dict = {}
    for cell_type in growth_rate_df[cell_type_col].unique():
        tmp_df = growth_rate_df[(growth_rate_df[cell_type_col]==cell_type)  & (growth_rate_df['GrowthRate'].isna()==False)]
        if method == "ols":
            ols_result = stats.linregress(x=tmp_df[cell_type_col], y=tmp_df[fraction_col])
            best_fit_func = lambda x: (ols_result.slope * x) + ols_result.intercept
            coeffs_dict[cell_type] = [best_fit_func(0), best_fit_func(1)]
        if method == "theil":
            theil_result = stats.theilslopes(x=tmp_df[fraction_col], y=tmp_df[growth_rate_col], alpha=ci)
            best_fit_func = lambda x: (theil_result[0] * x) + theil_result[1]
            coeffs_dict[cell_type] = [best_fit_func(0), best_fit_func(1), theil_result.intercept, theil_result.slope]
    # Transform into pay-off matrix entries. To do so, we need to find out the direction of the x-axis (i.e. whether
    # it's increasing for Type 1 or Type 2 as we go left to right).
    # The growth rate of the "index" population should be nan when their fraction is 0.
    no_deteced_growth_rate_df = growth_rate_df[growth_rate_df[growth_rate_col].isna()]
    avg_frac_when_no_growth_rate = no_deteced_growth_rate_df.groupby(cell_type_col).mean(numeric_only=True)[fraction_col]
    index_cell_type = avg_frac_when_no_growth_rate.idxmin()
    # Now we can compute the pay-off matrix entries
    cell_type_list = growth_rate_df[cell_type_col].unique() if cell_type_list is None else cell_type_list
    params_dict = {}
    for i, cell_type in enumerate(cell_type_list):
        pop_id = i + 1 # The population ID is 1-indexed (i.e. Type 1 and Type 2)
        if cell_type == index_cell_type:
            # The index cell type is the one whose self-interaction happens at fraction = 1
            params_dict["p%d%d"%(pop_id, pop_id)] = coeffs_dict[cell_type][1]
            params_dict["p%d%d"%(pop_id, pop_id%2+1)] = coeffs_dict[cell_type][0]
            params_dict["r%d"%pop_id] = coeffs_dict[cell_type][2] + coeffs_dict[cell_type][3]
            params_dict["c%d%d"%(pop_id%2+1, pop_id)] = - coeffs_dict[cell_type][3]
        else:
            params_dict["p%d%d"%(pop_id, pop_id)] = coeffs_dict[cell_type][0]
            params_dict["p%d%d"%(pop_id, pop_id%2+1)] = coeffs_dict[cell_type][1]
            params_dict["r%d"%pop_id] = coeffs_dict[cell_type][2]
            params_dict["c%d%d"%(pop_id%2+1, pop_id)] = coeffs_dict[cell_type][3]
    # Compute the game space position
    params_dict['Advantage_0'] = params_dict['p12'] - params_dict['p22']
    params_dict['Advantage_1'] = params_dict['p21'] - params_dict['p11']
    # Return the pay-off matrix entries
    return params_dict