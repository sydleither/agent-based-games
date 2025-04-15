from spatial_egt.data_processing.spatial_statistics.custom import nc_dist, proportion_s, sfp_dist
from spatial_egt.data_processing.spatial_statistics.muspan_statistics import (
    anni,
    cpcf,
    cross_k,
    entropy,
    global_moransi,
    j_function,
    kl_divergence,
    local_moransi_dist,
    nn_dist,
    qcm,
    wasserstein,
)
from spatial_egt.data_processing.spatial_statistics.muspan_patches import (
    create_patches,
    area_dist,
    circularity_dist,
    fractal_dimension_dist,
    patch_count,
)


STATISTIC_REGISTRY = {
    # Custom
    "NC_Resistant": nc_dist,
    "NC_Sensitive": nc_dist,
    "Proportion_Sensitive": proportion_s,
    "SFP": sfp_dist,
    # MuSpAn
    "ANNI_Resistant": anni,
    "ANNI_Sensitive": anni,
    "Entropy": entropy,
    "CPCF_Resistant": cpcf,
    "CPCF_Sensitive": cpcf,
    "Cross_Ripleys_k_Resistant": cross_k,
    "Cross_Ripleys_k_Sensitive": cross_k,
    "Global_Morans_i_Resistant": global_moransi,
    "Global_Morans_i_Sensitive": global_moransi,
    "J_Function_Resistant": j_function,
    "J_Function_Sensitive": j_function,
    "KL_Divergence": kl_divergence,
    "Local_Morans_i_Resistant": local_moransi_dist,
    "Local_Morans_i_Sensitive": local_moransi_dist,
    "NN_Resistant": nn_dist,
    "NN_Sensitive": nn_dist,
    "SES": qcm,
    "Wasserstein": wasserstein,
}

STATISTIC_PARAMS = {
    "in_silico": {
        "NC_Resistant": {"radius": 3, "return_fs": True},
        "NC_Sensitive": {"radius": 3, "return_fs": False},
        "SFP": {"sample_length": 5},
        "ANNI_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "ANNI_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "Cross_Ripleys_k_Resistant": {
            "max_radius": 6,
            "step": 1,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "Cross_Ripleys_k_Sensitive": {
            "max_radius": 6,
            "step": 1,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "CPCF_Sensitive": {
            "max_radius": 5,
            "annulus_step": 1,
            "annulus_width": 3,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "CPCF_Resistant": {
            "max_radius": 5,
            "annulus_step": 1,
            "annulus_width": 3,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "Global_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 5},
        "Global_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 5},
        "J_Function_Resistant": {"cell_type": "resistant", "radius_step": 1},
        "J_Function_Sensitive": {"cell_type": "sensitive", "radius_step": 1},
        "KL_Divergence": {"mesh_step": 3},
        "Local_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 5},
        "Local_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 5},
        "NN_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "NN_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "Patches": {"alpha": 1},
        "SES": {"side_length": 10},
    },
    "in_vitro": {
        "NC_Resistant": {"radius": 30, "return_fs": True},
        "NC_Sensitive": {"radius": 30, "return_fs": False},
        "SFP": {"sample_length": 50},
        "ANNI_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "ANNI_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "Cross_Ripleys_k_Resistant": {
            "max_radius": 60,
            "step": 10,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "Cross_Ripleys_k_Sensitive": {
            "max_radius": 60,
            "step": 10,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "CPCF_Sensitive": {
            "max_radius": 50,
            "annulus_step": 10,
            "annulus_width": 30,
            "cell_type1": "sensitive",
            "cell_type2": "resistant",
        },
        "CPCF_Resistant": {
            "max_radius": 50,
            "annulus_step": 10,
            "annulus_width": 30,
            "cell_type1": "resistant",
            "cell_type2": "sensitive",
        },
        "Global_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Global_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "J_Function_Resistant": {"cell_type": "resistant", "radius_step": 10},
        "J_Function_Sensitive": {"cell_type": "sensitive", "radius_step": 10},
        "Local_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Local_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "NN_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "NN_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "Patches": {"alpha": 10},
        "SES": {"side_length": 100},
    },
}

DOMAIN_REGISTRY = {"Patches": create_patches}

DOMAIN_PARAMS = {"in_silico": {"Patches": {"alpha": 1}}, "in_vitro": {"Patches": {"alpha": 10}}}

DOMAIN_STATISTIC_REGISTRY = {
    "Patch_Area": area_dist,
    "Patch_Circularity": circularity_dist,
    "Patch_Fractal_Dimension": fractal_dimension_dist,
    "Patch_Count": patch_count,
}

DOMAIN_STATISTIC_PARAMS = {}

FUNCTION_LABELS = {
    "NC_Resistant": {"x": "Fraction Sensitive in Neighborhood", "y": "Fraction of Resistant Cells"},
    "NC_Sensitive": {"x": "Fraction Resistant in Neighborhood", "y": "Fraction of Sensitive Cells"},
    "SFP": {"x": "Fraction Sensitive", "y": "Frequency Across Subsamples"},
    "CPCF_Resistant": {"x": "r", "y": "g(r)"},
    "CPCF_Sensitive": {"x": "r", "y": "g(r)"},
    "Cross_Ripleys_k_Resistant": {"x": "r", "y": "g(r)"},
    "Cross_Ripleys_k_Sensitive": {"x": "r", "y": "g(r)"},
    "J_Function_Resistant": {"x": "r", "y": "j(r)"},
    "J_Function_Sensitive": {"x": "r", "y": "j(r)"},
    "Local_Morans_i_Resistant": {"x": "Moran's i", "y": "Proportion"},
    "Local_Morans_i_Sensitive": {"x": "Moran's i", "y": "Proportion"},
    "NN_Resistant": {"x": "Distance", "y": "Proportion"},
    "NN_Sensitive": {"x": "Distance", "y": "Proportion"},
    "Patch_Area": {"x": "Patch Area", "y": "Proportion"},
    "Patch_Circularity": {"x": "Patch Circularity", "y": "Proportion"},
    "Patch_Fractal_Dimension": {"x": "Patch Fractal Dimension", "y": "Proportion"},
}

DISTRIBUTION_BINS = {
    "NC_Resistant": (0, 1.1, 0.1),
    "NC_Sensitive": (0, 1.1, 0.1),
    "SFP": (0, 1.1, 0.1),
    "Local_Morans_i_Resistant": (-5, 5.5, 0.5),
    "Local_Morans_i_Sensitive": (-5, 5.5, 0.5),
    "NN_Resistant": (1, 5, 0.2),
    "NN_Sensitive": (1, 5, 0.2),
    "Patch_Area": (0, 21, 1),
    "Patch_Circularity": (0, 1.1, 0.1),
    "Patch_Fractal_Dimension": (0, 11, 1),
}
