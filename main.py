from ui.frame import Frame, build_default_bootstrap_datas
from ui.frame_config import FrameConfig








def _default_initial_scramble_groups(size,puzzle_type):
    """起動時に登録する既定の scramble 候補群を返す。"""
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
            
    if size == 3:
        return (
            [
                (" U ",),
                (" U'",),
                (" U2",),
                (" F ",),
                (" F'",),
                (" F2",),
                (" R ",),
                (" R'",),
                (" R2",),
                (" U ",),
                (" U'",),
                (" U2",),
                (" x'"," z'"),
                (" x "," z'"),
                (" x'"," z "),
                (" x "," z "),
                (" z "," x "),
                (" z'"," x "),
                (" z "," x'"),
                (" z'"," x'"),
                (" U2"," R "," U "," R'"," U'"," F'"," U "," F "," U2"),
                (" U2"," F'"," U'"," F "," U "," R "," U'"," R'"," U2"),
                (" U2"," R "," U "," R'"," U'"," F'"," U "," F "," U2") * 3,
                (" U2"," F'"," U'"," F "," U "," R "," U'"," R'"," U2") * 3,
                (" U2"," R "," U "," R'"," U'"," F'"," U "," F "," U2") * 5,
                (" U2"," F'"," U'"," F "," U "," R "," U'"," R'"," U2") * 5,

                (" R'", ' U ', ' R ', ' U ', " F'", " U'", ' B ', " F'", ' L ', ' F ', " L'", " B'", ' F ', " R'", " U'", ' R '),
                (" R'", ' U ', ' R ', " F'", ' B ', ' L ', " F'", " L'", ' F ', " B'", ' U ', ' F ', " U'", " R'", " U'", ' R '),                



            ],
            [
                (" U'"," R'"," U "," R'"," U'"," F'"," U "," F "," R2"," U "),
                (" U "," F "," U'"," F "," U "," R "," U'"," R'"," F2"," U'"),
                (" R'"," F "," U2"," F'"," R "," F "," R'"," U2"," R "," F'"),
                (' R2', ' F2', ' U2', ' R ', ' U2', ' R2', ' F2', ' R ', ' U2', ' R2', ' U2', ' F2', ' R ', ' F2'),
                (" R "," U "," R'"," U "," R "," U2"," R'"),
                (' F ', " L'", ' B ', ' L ', " F'", " L'", " B'", " L'", " B'", " L'", ' B ', " L'", ' D2', ' R ', " F'", " R'", ' D2'),
                (' L ', ' U2', " L'", ' F ', ' D2', " F'", ' L ', ' U2', " L'", ' F ', ' D2', " F'"),
                (' F2', ' D ', ' F ', " D'", ' F ', ' L2', " B'", ' U ', ' B ', " L'", ' D ', " L'", ' U ', ' L ', " D'", " L'", " U'"),
                (" E "," F "," E "," F'"," E "," F'"," E "," F "," E "),
                (" E'"," F "," E'"," F'"," E'"," F'"," E'"," F "," E'"),
                (" F "," R "," U'"," R'"," U'"," R "," U "," R'"," F'"," R "," U "," R'"," U'"," R'"," F "," R "," F'"),
                (' M2', ' U ', ' M ', ' U2', " M'", ' U ', " M'", " U'", ' F2', ' U ', ' M ', " U'", ' F2', ' U ', ' M2'),
                

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
                (" R'",),
                (" F ",),
                (" F'",),
                (" U ",),
                (" U'",),
                (" R "," U "," R'"),
                (" F'"," U "," F "),
                (" R "," U'"," R'"),
                (" F'"," U'"," F "),
            ],
            [
                (" R "," U ","2R2"," U'"," R'"," U ","2R2"," U'"),
                (" F'"," U ","2F2"," U'"," F "," U ","2F2"," U'"),
                ("2R ","2F'","2R'","2F "),
                ("2R ","3F'","2R'","3F "),
                ("2R "," S'","2R'"," S "),
                ("2F'","2R ","2F ","2R'"),
                ("3F'","2R ","3F ","2R'"),
                (" S'","2R "," S ","2R'"),
                (" M "," U "," M2"," U2"," M2"," U "," M'"),
                (" S "," U "," S2"," U2"," S2"," U "," S'"),
                (" R "," F "," R'"," B2"," R "," F'"," R'"," B2"),
                (" F "," R "," F'"," L2"," F "," R'"," F'"," L2"),
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            )


def build_default_frame_config():
    """現在の既定実験設定を FrameConfig として返す。"""
    ai_search_modes = ['search2'] * 10 + ['search3'] * 10
    lrs = [2.0e-6] * 2 + [5.0e-7] * 6 + [2.0e-6] * 2 + [5.0e-6] * 2 + [5.0e-6] * 6 + [5.0e-6] * 2
    wdlrs = [1.0e-7] * 10 + [5.0e-5] * 10
    skip_search = [True] * 10 + [False] * 10
    weight_decay = [True] * 20
    search3_progress = [False] * 20
    for i in range(2,8):
        weight_decay[i] = False
        search3_progress[10 + i] = True

    adam = weight_decay.copy()

    cube_size = 7
    puzzle_type = 'cube'
    if cube_size >= 7:
        transform_idx = [0,0,48,48,48,48,48,48,0,0] * 2
    else:
        transform_idx = [0] * 20

    if puzzle_type == 'megaminx':
        priority_list = [['Corner', 'MidEdge']] * 20
        bootstrap_datas = None
    else:
        priority_list = [
            ['CoreCenter','ObliqueCenter-A','PlusCenter-Layer2','XCenter-Layer2','ObliqueCenter-B','PlusCenter-Layer3','XCenter-Layer3','Wing-Layer2','Wing-Layer3','Corner','MidEdge'],
            ['Wing-Layer3','Wing-Layer2','MidEdge','Corner','XCenter-Layer2','PlusCenter-Layer2','ObliqueCenter-A','XCenter-Layer3','PlusCenter-Layer3','ObliqueCenter-B','CoreCenter'],
        ] * 10
        bootstrap_datas = build_default_bootstrap_datas(cube_size = cube_size)

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
        lr_vs = [0.99] * 20,
        lr_hs = [0.99] * 20,
        out_cs = [1.0] * 20,
        search3_cs = [0.05] * 20,
        pv_ratios = [20.0] * 10 + [20.0] * 10,
        ##transform_idx = [0,1,50,3,52,5,54,7,56,64] * 2,
        ##flip_inside_idx = [False,False,True,False,True,False,True,False,True,True] * 2,
        transform_idx = transform_idx,
        flip_inside_idx = [False,True] * 10,
        priority_list = priority_list,
        bootstrap_datas = bootstrap_datas,
    )


if __name__ == '__main__':
    config = build_default_frame_config()
    F = Frame(config = config)
    F.pack()
    F.mainloop()
