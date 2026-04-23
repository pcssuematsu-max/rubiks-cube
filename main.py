from ui.frame import Frame, build_default_bootstrap_datas
from ui.frame_config import FrameConfig


def _default_initial_scramble_groups():
    """起動時に登録する既定の scramble 候補群を返す。"""
    return (
        [("2F ","3R ","2F'"," E ","3R'"," S "," E'"," S'"),
         (" R2","2F ","3R ","2F'"," R2"," E ","3R'"," S "," E'"," S'"),
         ("3R ","2F ","3R ","2F'"," E ","3R2"," S "," E'"," S'"),
         (" R2","3R ","2F ","3R ","2F'"," R2"," E ","3R2"," S "," E'"," S'"),
         ("3R2","2F ","3R ","2F'"," E ","3R "," S "," E'"," S'"),
         (" R2","3R2","2F ","3R ","2F'"," R2"," E ","3R "," S "," E'"," S'"),
         (" E "," F "," E "," F'"," E "," F'"," E "," F "," E'"," M "," E2"," M'"),
         (" E "," F "," E "," F'"," E "," F'"," E "," F "," E'"," S "," E2"," S'"),
         (" F "," E "," F "," E "," F'"," E "," F'"," E "," F "," E "," F'"," E2"," M "," E2"," M'"),
         (" F "," E "," F "," E "," F'"," E "," F'"," E "," F "," E "," F'"," E2"," S "," E2"," S'"),
         (" F'"," E "," F "," E "," F'"," E "," F'"," E "," F "," E "," F "," E2"," M "," E2"," M'"),
         (" F'"," E "," F "," E "," F'"," E "," F'"," E "," F "," E "," F "," E2"," S "," E2"," S'"),
         (" E "," F "," E "," F'"," E "," F "," E "," F'"," E'"," M "," E2"," M'"),
         (" E "," F "," E "," F'"," E "," F "," E "," F'"," E'"," S "," E2"," S'"),
         (" E "," F'"," E "," F "," E "," F'"," E "," F "," E'"," M "," E2"," M'"),
         (" E "," F'"," E "," F "," E "," F'"," E "," F "," E'"," S "," E2"," S'"),
         (" E "," F "," E "," F "," E "," F "," E "," F "," E'"," M "," E2"," M'"),
         (" E "," F "," E "," F "," E "," F "," E "," F "," E'"," S "," E2"," S'"),
         (" E "," F'"," E "," F'"," E "," F'"," E "," F'"," E'"," M "," E2"," M'"),
         (" E "," F'"," E "," F'"," E "," F'"," E "," F'"," E'"," S "," E2"," S'"),
         (" U ","2F "," D ","2F'"," U'","2F "," D'","3R ","2F'","3R'"),
         ("2F2"," U ","2F "," D ","2F'"," U'","2F "," D'","3R ","2F ","3R'"),
         ("2F "," U ","2F "," D ","2F'"," U'","2F "," D'","3R ","2F2","3R'"),
         ("2R ","2F ","2R'","3R ","2F ","3R'","2F2"),
         ("2R ","2F'","2R'","3R ","2F'","3R'","2F2"),
         ("2R ","2F ","2R'","3R ","2F2","3R'","2F "),
         ("2R ","2F'","2R'","3R ","2F2","3R'","2F'"),
         ("2R ","2F2","2R'","3R ","2F ","3R'","2F "),
         ("2R ","2F2","2R'","3R ","2F'","3R'","2F'"),
         ("3R ","2F ","3R'","2R ","2F ","2R'","2F2"),
         ("3R ","2F'","3R'","2R ","2F'","2R'","2F2"),
         ("3R ","2F ","3R'","2R ","2F2","2R'","2F "),
         ("3R ","2F'","3R'","2R ","2F2","2R'","2F'"),
         ("3R ","2F2","3R'","2R ","2F ","2R'","2F "),
         ("3R ","2F2","3R'","2R ","2F'","2R'","2F'"),
         ("2U "," F2","2D2"," F2","2U'"," R2","2D "," R2"),
         ("2U2"," F2"," R2","2D "," R2","2D2"," F2"),
         ("3U "," B2"," F2","3D2"," R2","3U "," R2","3D "," F2","3U'"," B2"),
         ("3D2"," B2"," R2"," F2","3U "," F2","3U "," R2","3U'"," B2"),
         ("2U "," F2","2U "," F2","2U "," F2","2U "," F2","2U "),
         ("3U "," R2","3U "," R2","3U "," R2","3U "," R2","3U "),
         ("2U "," F2","2U'"," B2","2U "," F2","2U'"," B2"),
         (" R2","3U "," L2","3U'"," R2","3U "," L2","3U'",)
         ],
        [],
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
    lrs = [2.0e-6] * 20
    wdlrs = [1.0e-6] * 20
    skip_search = [True] * 10 + [False] * 10
    weight_decay = [True] * 20
    for i in range(2,8):
        weight_decay[i] = False

    return FrameConfig(
        cube_size = 7,
        ai_search_modes = ai_search_modes,
        initial_scramble_groups = _default_initial_scramble_groups(),
        lrs = lrs,
        wdlrs = wdlrs,
        skip_search = skip_search,
        weight_decay = weight_decay,
        adam = weight_decay.copy(),
        lr_vs = [0.99] * 20,
        lr_hs = [0.99] * 20,
        out_cs = [1.0] * 20,
        search3_cs = [0.05] * 20,
        transform_idx = [0,1,50,3,52,5,54,7,56,64] * 2,
        flip_inside_idx = [False,False,True,False,True,False,True,False,True,True] * 2,
        priority_list = [
            ['CoreCenter','ObliqueCenter-A','PlusCenter-Layer2','XCenter-Layer2','ObliqueCenter-B','PlusCenter-Layer3','XCenter-Layer3','Wing-Layer2','Wing-Layer3','Corner','MidEdge'],
            ['Wing-Layer3','Wing-Layer2','MidEdge','Corner','XCenter-Layer2','PlusCenter-Layer2','ObliqueCenter-A','XCenter-Layer3','PlusCenter-Layer3','ObliqueCenter-B','CoreCenter'],
        ] * 10,
        bootstrap_datas = build_default_bootstrap_datas(cube_size = 7),
    )


if __name__ == '__main__':
    config = build_default_frame_config()
    F = Frame(config = config)
    F.pack()
    F.mainloop()
