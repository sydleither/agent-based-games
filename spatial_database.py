from spatial_egt.data_processing.spatial_statistics.custom import (
    nc_dist,
    proportion_cell,
    spatial_subsample_dist,
)
from spatial_egt.data_processing.spatial_statistics.muspan_statistics import (
    anni,
    cpcf,
    cross_k,
    entropy,
    global_moransi,
    kl_divergence,
    local_moransi_dist,
    nn_dist,
    qcm,
    wasserstein,
)

STATISTIC_REGISTRY = {
    # Custom
    "NC_Resistant": nc_dist,
    "NC_Sensitive": nc_dist,
    "Proportion_Sensitive": proportion_cell,
    "Spatial_Subsample": spatial_subsample_dist,
    # MuSpAn
    "ANNI_Resistant": anni,
    "ANNI_Sensitive": anni,
    "CPCF_RR": cpcf,
    "CPCF_RS": cpcf,
    "CPCF_SR": cpcf,
    "CPCF_SS": cpcf,
    "Ripleys_k_RR": cross_k,
    "Ripleys_k_RS": cross_k,
    "Ripleys_k_SR": cross_k,
    "Ripleys_k_SS": cross_k,
    "Entropy": entropy,
    "Global_i_Resistant": global_moransi,
    "Global_i_Sensitive": global_moransi,
    "KL_Divergence": kl_divergence,
    "Local_i_Resistant": local_moransi_dist,
    "Local_i_Sensitive": local_moransi_dist,
    "NN_RR": nn_dist,
    "NN_RS": nn_dist,
    "NN_SR": nn_dist,
    "NN_SS": nn_dist,
    "SES": qcm,
    "Wasserstein": wasserstein,
}

STATISTIC_PARAMS = {
    "in_vitro_pc9": {
        "NC_Resistant": {"radius": 50, "return_fs": True},
        "NC_Sensitive": {"radius": 50, "return_fs": False},
        "Proportion_Sensitive": {"cell_type": "sensitive"},
        "Spatial_Subsample": {"sample_length": 50},
        "ANNI_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "ANNI_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "CPCF_RR": {
            "max_radius": 100,
            "annulus_step": 10,
            "annulus_width": 10,
            "cell_type1": "resistant",
            "cell_type2": "resistant",
        },
        "CPCF_RS": {
            "max_radius": 100,
            "annulus_step": 10,
            "annulus_width": 10,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "CPCF_SR": {
            "max_radius": 100,
            "annulus_step": 10,
            "annulus_width": 10,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "CPCF_SS": {
            "max_radius": 100,
            "annulus_step": 10,
            "annulus_width": 10,
            "cell_type1": "sensitive",
            "cell_type2": "sensitive",
        },
        "Ripleys_k_RR": {
            "max_radius": 100,
            "step": 10,
            "cell_type1": "resistant",
            "cell_type2": "resistant",
        },
        "Ripleys_k_RS": {
            "max_radius": 100,
            "step": 10,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "Ripleys_k_SR": {
            "max_radius": 100,
            "step": 10,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "Ripleys_k_SS": {
            "max_radius": 100,
            "step": 10,
            "cell_type1": "sensitive",
            "cell_type2": "sensitive",
        },
        "Global_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Global_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "KL_Divergence": {"mesh_step": 100},
        "Local_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Local_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "NN_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "NN_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "SES": {"side_length": 100},
    },
}
STATISTIC_PARAMS["in_vitro_h358"] = STATISTIC_PARAMS["in_vitro_pc9"]

grid_reduction = 16
in_silico = {}
for spatial_stat in STATISTIC_PARAMS["in_vitro_pc9"]:
    stat_params = STATISTIC_PARAMS["in_vitro_pc9"][spatial_stat]
    in_silico[spatial_stat] = {}
    for k,v in stat_params.items():
        if isinstance(v, str) or isinstance(v, bool):
            in_silico[spatial_stat][k] = v
        else:
            in_silico[spatial_stat][k] = round(v*(grid_reduction/100))
STATISTIC_PARAMS["in_silico"] = in_silico
