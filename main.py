from ui.frame import Frame, build_default_bootstrap_datas
from ui.frame_config import FrameConfig


if __name__ == '__main__':
    ai_search_modes = ['search2'] * 10 + ['search3'] * 10
    initial_scramble_groups = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    lrs = [2.0e-6] * 20
    wdlrs = [1.0e-6] * 20
    skip_search = [True] * 10 + [False] * 10 
    weight_decay = [True] * 20
    for i in range(2,8):
        weight_decay[i] = False
    
    adam = weight_decay.copy()
    lr_vs = [0.99] * 20
    lr_hs = [0.99] * 20
    out_cs = [1.0] * 20
    search3_cs = [0.05] * 20
    transform_idx = [0,1,50,3,52,5,54,7,56,64] * 2
    flip_inside_idx = [False,False,True,False,True,False,True,False,True,True] * 2
    priority_list = [
    ['CoreCenter','ObliqueCenter-A','PlusCenter-Layer2','XCenter-Layer2','ObliqueCenter-B','PlusCenter-Layer3','XCenter-Layer3','Wing-Layer2','Wing-Layer3','Corner','MidEdge'],
    ['Wing-Layer3','Wing-Layer2','MidEdge','Corner','XCenter-Layer2','PlusCenter-Layer2','ObliqueCenter-A','XCenter-Layer3','PlusCenter-Layer3','ObliqueCenter-B','CoreCenter'],
    ] * 10
    bootstrap_datas = build_default_bootstrap_datas(cube_size = 7)



    config = FrameConfig(
        cube_size = 7,
        ai_search_modes = ai_search_modes,
        initial_scramble_groups = initial_scramble_groups,
        lrs = lrs,
        wdlrs = wdlrs,
        skip_search = skip_search,
        weight_decay = weight_decay,
        adam = adam,
        lr_vs = lr_vs,
        lr_hs = lr_hs,
        out_cs = out_cs,
        search3_cs = search3_cs,
        transform_idx = transform_idx,
        flip_inside_idx = flip_inside_idx,
        priority_list = priority_list,
        bootstrap_datas = bootstrap_datas,
    )

    F = Frame(config = config)
    F.pack()
    F.mainloop()
