from ui.frame import Frame, build_default_bootstrap_datas
from ui.frame_config import FrameConfig

def _default_initial_scramble_groups(size,puzzle_type):
    """起動時に登録する既定の scramble 候補群を返す。"""
    if puzzle_type == "square1":
        return (
            [
                ((0, 0, "/"),),
                ((1, 0, None),),
                ((0, 1, None),),
                ((1, 1, "/"),),
                ((3, -2, "/"),),
                ((-3, 3, "/"),),
                ((-2, 0, "/"),),
                ((0, 3, "/"),),
                ((1, 1, "/"),(6,6,None)),
                ((3, -2, "/"),(6,6,None)),
                ((-3, 3, "/"),(6,6,None)),
                ((-2, 0, "/"),(6,6,None)),
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    if puzzle_type == "skewb":
        return (
            [
                ("URF",),
                ("ULB",),
                ("UBR","ULB'","UBR'","ULB","UFL","URF'","UFL'","URF"),
                ("UFL'", 'ULB', "UFL'", "URF'", "UFL'", 'URF', 'UBR', "ULB'", "UBR'", 'ULB'),
                ("DRB'", 'DBL', 'DRB', 'DFR', 'DFL', 'DBL', "DFR'", "DBL'", "DFR'", "DFL'"),
                ("UBR'","ULB'","UBR'","ULB","UFL","URF'","UFL'","URF","UBR'"),
                ("DRB'", 'DBL', 'DRB', "DBL'", "DFR'", "DRB'", 'DFR', 'DRB', 'DBL', "DRB'", "DBL'", "DFR'", 'DRB', 'DFR'),
                ('DRB', 'UBR', "ULB'", 'DRB', "UBR'", "ULB'", "UBR'", "ULB'", 'UBR'),
                ('UBR', "ULB'", 'UBR', "ULB'", "UBR'", 'ULB', "UBR'", 'ULB'),
                ("DRB'", "DBL'", "ULB'", 'UFL', "URF'", "ULB'", "UBR'", 'ULB', "UBR'", "ULB'", "UFL'", 'ULB'),
                ("URF'", 'DFL', "DFR'", "DFL'", 'URF', "UBR'", 'UFL', "URF'", 'UFL', 'URF', 'UFL', "URF'", "UFL'", 'URF', "ULB'", 'UBR', 'ULB', "UBR'"),
                ("URF'", 'DFL', "DFR'", "DRB'", "DFL'", "ULB'", 'URF', "UBR'", "UFL'", "ULB'"),

            ],
            [
            ],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    if puzzle_type == "pyraminx":
      return (
            [
                ("R", "U", "R'", "U'"),
                ("L'", "U'", "L", "U"),
                ("R", "L'", "R'", "L"),
                ("U", "R", "U'", "R'"),
                ('U', 'R','U', "R'", 'U', 'R', 'U', "R'","u'"),
                ('L', 'R', 'U', "R'", "U'", "L'"),
                ('R', "L'", 'U', 'L', "U'", "R'"),
                ("R'","L","R","L'","U","L'","U'","L"),
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    if puzzle_type == "master_pyraminx":
      return (
            [
                ("3L","3R","3L'","3R'"),
                ("3L","3R'","3L'","3R"),
                ('3R', '3B', 'L', '3B', "3U'", "R'", "3L'", "3B'", "3R'", 'L', "3U'", "3B'", "3L'", "U'", '3R'),



            ],
            [
                ("u",),
                ("l",),
                ("R","3U","R'","3U'"),
                
            ],
            [

            ],
            [],
            [],
            [],
            [],
            [],
        )


    if puzzle_type == "megaminx":
        return (
            [("U",),
             ("U'",),
             ("U2",),
             ("U2'",),
             ("D",),
             ("B",),
             ("dL",),
             ("dR",),
             ("sL",),
             ("sR",),
             ("R",),
             ("R'",),
             ("F",),
             ("F'",),



            ],
            [
                ("F2", "R2'", "F'", "R", "F", "R", "F2'","L'", "U'", "R'", "U", "R", "L"),
                ("R","U","L","U'","R'","U","L'","U'"),
                ('L2', "U'", "R'", 'U', 'L', "U'", 'R', 'U', 'L2'),
                ("R'", "F'", 'R', 'bR', "R'", 'F2', 'R', "bR'", "R'", "F'", 'R'),
                ('bR', "U'", "L'", 'U', "bR'", "R'", 'bR', "U'", 'L', 'U', "bR'", 'R'),
                ('bL', "F'", "L'", "bL'", 'L', 'F', "L'", 'R', 'bR', 'bL', 'L', "bL'", "bR'", "R'"),
                ('bR2', "U'", "L'", 'U', 'bR2', "R'", 'bR', "U'", 'L', 'U', "bR'", 'R', 'bR'),
                ("F'", "L'", 'F', "R2'", "F'", 'L', 'F', 'R2'),
                ('R', 'U', "L'", "U'", 'bR', "R'", 'U', 'L', "U'", 'R', "bR'", "R'"),
            ],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    if puzzle_type == "fto":
        return (
            [   
                ("URF",),
                ("URF'",),
                ("UFL",),
                ("UFL'",),
                          
            ],
            [
                ("UFL'", 'DFR', "UFL'", "DFR'", "UFL'", 'DFR', "UFL'", "DFR'", "DRB'", 'DLF', 'DRB', "mUBR'", "DRB'", "DLF'", 'DRB', 'UBR', 'DBL', "UBR'", 'DBL', 'UBR', 'DBL', "UBR'", 'DBL', 'mUBR'),
                ("UBR'", 'UFL', "UBR'", "UFL'", "UBR'", 'UFL', "UBR'", "UFL'", 'mURF', "UFL'", 'DBL', "UFL'", "DBL'", "UFL'", 'DBL', "UFL'", "DBL'", "DLF'", 'URF', 'DLF', "mURF'", "DLF'", "URF'", 'DLF', 'DFR', 'UBR', "DFR'", 'UBR', 'DFR', 'UBR', "DFR'", 'UBR'),
                ('mUBR', "UFL'", 'UBR', 'UFL', "mUBR'", "UBR'", "DBL'", "UBR'", 'DBL', 'DFR', 'UBR', "mULB'", "UBR'", "DFR'", 'UBR', 'mULB'),
                ('DBL', 'UBR', 'DBL', "UBR'", 'DBL', "mULB'", "UBR'", 'DFR', 'UBR', 'mULB', "UBR'", "DFR'", 'UBR', "mUFL'", 'UBR', "UFL'", "UBR'", 'mUFL', 'UBR', 'UFL', "UBR'", 'mUFL', "UBR'", "UFL'", 'UBR', "mUFL'", "UBR'", 'UFL', 'UBR'),
  
            ],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    if puzzle_type == "cto":
        return (
            [
                ("U", "R", "U'", "R'"),
                ("U", "R'", "U'", "R"),
                ("R", "U", "R'", "U", "R", "U2", "R'"),
                ('U', "R'", 'U2', 'R', 'U'),
                ('U2', "R'", "U'", 'R', "U'"),
                ("U'", 'R2', "U'", 'R2', 'U2'),
                ('R', "U'", "R'", 'u', "U'", 'R', "U'", "R'", 'U2'),
                ("F","R","U","R'","U'","F'"),
                ("R'","F","R","F'","U","F'","U'","F"),
                ('U', 'R', 'U', "R'", 'U2'),
                ('F', "U'", 'R', 'U', "R'", "F'"),
                ("u'", 'R2', 'U', 'R2', 'U2', 'R2', 'U', 'R2', 'U'),
                ('U2', 'R', 'U2', "R'", 'U', 'R', 'U2', "R'", 'U2', 'u2', 'R', 'U', "R'"),
                ("u'", 'R', 'U', "R'", 'U', 'R', 'U', "R'", 'U2'),
                ('U2', 'R', "U'", "R'", 'U', 'R', 'U', "R'", 'U', 'R', "U'", "R'", 'u'),
                ("R'", 'U', 'R', "U'", 'R', 'U', 'R', "U'", "R'", "r'"),
                ("U'", "R'", 'U', "R'", "U'", "R'", 'U', "R'", "U'", "R'", 'U', 'r'),
                ('R2', "U'", 'R2', 'u', "U'", 'R2', "U'", 'R2', 'U2'),
                ('F', "L'", 'F', 'L', "F'", 'D', "F'", "L'", "D'", 'L', "D'", 'B', 'D', "B'"),
                ('D', 'B', 'D', "B'", 'D2', 'B', 'D', "B'", "d'", 'F', 'D', 'F', "D'", 'F', 'D', 'F', "D'", 'F', "f'"),

                
            ],
            [
            ],
            [],
            [],
            [],
            [],
            [],
            [],
        )
            
    if size == 3:
        return (
            [

            ],
            [
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            )
    elif size == 7:
        return (
            [
                (" R ",),
                ("2R ",),
                (" M'",),
                (" U ",),
                ("2U ",),
                (" E'",),

            ],
            [
            ],
            [
            ],
            [
            ],
            [],
            [],
            [],
            [],
            )


def build_default_frame_config():
    """現在の既定実験設定を FrameConfig として返す。"""
    ai_search_modes = [
        'search2'
        if ai_index < 10
        else 'search2'
        for ai_index in range(20)
    ]
    original_transformer_attention = [False] * 10 + [True] * 10
    ai_count = len(ai_search_modes)
    is_search2_ai = [mode.startswith('search2') for mode in ai_search_modes]
    lrs = [
        2.0e-6 if original_transformer_attention[ai_index] else (2.0e-6 if is_search2_ai[ai_index] else 1.0e-6)
        for ai_index in range(ai_count)
    ]
    wdlrs = [
        1.0e-7 if original_transformer_attention[ai_index] else (1.0e-7 if is_search2_ai[ai_index] else 1.0e-5)
        for ai_index in range(ai_count)
    ]
    skip_search = [is_search2_ai[ai_index] for ai_index in range(ai_count)]
    weight_decay = [True] * ai_count
    search3_progress = [False] * 10 + [False,False,False,True,False,True,False,True,False,False]
    residuals = list(range(ai_count))
    search2_value_loss_types = ['myloss','myloss','myloss2','myloss2','myloss2','myloss2','myloss2','myloss2','myloss','myloss'] * 2
    search2_value_loss_margins = [5.0] * ai_count

    adam = weight_decay.copy()

    cube_size = 7
    puzzle_type = 'cube'
    if cube_size >= 7:
        transform_idx = [0,49,50,3,52,5,54,7,24,25] * 2
        flip_inside_idx = [False,True] * 10
    else:
        transform_idx = [0,1,2,3,4,5,6,7,24,25] * 2
        flip_inside_idx = [False] * ai_count


    if puzzle_type == 'megaminx':
        priority_list = [['Corner', 'MidEdge']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
    elif puzzle_type == 'pyraminx':
        priority_list = [['Corner', 'Edge', 'Center']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    elif puzzle_type == 'master_pyraminx':
        priority_list = [['Corner', 'Edge', 'MidEdge', 'Center']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    elif puzzle_type == 'skewb':
        priority_list = [['Corner', 'Center']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    elif puzzle_type == 'square1':
        priority_list = [['Corner', 'Edge', 'Shape']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    elif puzzle_type == 'fto':
        priority_list = [['Corner', 'Edge', 'CenterA', 'CenterB']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    elif puzzle_type == 'cto':
        priority_list = [['Corner', 'Edge', 'Center']] * ai_count
        bootstrap_datas = None
        bootstrap_search3_datas = None
        transform_idx = [0] * ai_count
        flip_inside_idx = [False] * ai_count
    else:
        priority_list = [
            ['CoreCenter','ObliqueCenter-A','PlusCenter-Layer2','XCenter-Layer2','ObliqueCenter-B','PlusCenter-Layer3','XCenter-Layer3','Wing-Layer2','Wing-Layer3','Corner','MidEdge'],
            ['Wing-Layer3','Wing-Layer2','MidEdge','Corner','XCenter-Layer2','PlusCenter-Layer2','ObliqueCenter-A','XCenter-Layer3','PlusCenter-Layer3','ObliqueCenter-B','CoreCenter'],
        ] * 10
        bootstrap_datas = build_default_bootstrap_datas(cube_size = cube_size)
        bootstrap_search3_datas = None

    return FrameConfig(
        puzzle_type = puzzle_type,
        cube_size = cube_size,
        ai_search_modes = ai_search_modes,
        initial_scramble_groups = _default_initial_scramble_groups(cube_size,puzzle_type),
        transform_random = False,
        search3_progress = search3_progress,
        lrs = lrs,
        wdlrs = wdlrs,
        skip_search = skip_search,
        weight_decay = weight_decay,
        adam = adam,
        lr_vs = [0.99] * ai_count,
        lr_hs = [0.99] * ai_count,
        out_cs = [1.0] * ai_count,
        search3_cs = [0.05] * ai_count,
        search2_max_frontiers = [30000] * ai_count,
        search2_torch_batch_sizes = [
            64 if original_transformer_attention[ai_index] else 100
            for ai_index in range(ai_count)
        ],
        search2_value_loss_types = search2_value_loss_types,
        search2_value_loss_margins = search2_value_loss_margins,
        torch_training_devices = [
            'cpu' if original_transformer_attention[ai_index] else 'auto'
            for ai_index in range(ai_count)
        ],
        use_torch = [False] * ai_count,
        use_torch_predict = [
            bool(original_transformer_attention[ai_index])
            for ai_index in range(ai_count)
        ],
        use_torch_training = [
            bool(original_transformer_attention[ai_index])
            for ai_index in range(ai_count)
        ],
        residuals = residuals,
        update_scales = [
            (5.0, 1.0, 20.0) if is_search2_ai[ai_index] else (5.0, 1.0, 5.0)
            for ai_index in range(ai_count)
        ],
        original_transformer_attention = original_transformer_attention,
        original_transformer_attention_dims = [64] * ai_count,
        original_transformer_attention_token_modes = ['piece'] * ai_count,
        original_piece_attention_backward_chunk_sizes = [32] * ai_count,
        original_train_batch_sizes = [
            20 if original_transformer_attention[ai_index] else 100
            for ai_index in range(ai_count)
        ],
        original_train_state_batch_sizes = [
            16 if original_transformer_attention[ai_index] else 0
            for ai_index in range(ai_count)
        ],
        original_train_max_batches = [
            100 if original_transformer_attention[ai_index] else 0
            for ai_index in range(ai_count)
        ],
        original_train_recent_ratios = [
            1.0 if original_transformer_attention[ai_index] else 0.0
            for ai_index in range(ai_count)
        ],
        max_search2_data = 80000,
        max_search3_data_per_ai = 2000,
        transform_idx = transform_idx,
        flip_inside_idx = flip_inside_idx,
        priority_list = priority_list,
        bootstrap_datas = bootstrap_datas,
        bootstrap_search3_datas = bootstrap_search3_datas,
    )


if __name__ == '__main__':
    config = build_default_frame_config()
    F = Frame(config = config)
    F.pack()
    F.mainloop()
