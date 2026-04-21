#Rubiks_original

## 概要
このプログラムは、ルービックキューブを探索と多層ニューラルネットワークを用いて解かせるためのツールです。
独自のGreedy探索(Search2)、PUCTを用いた探索(Search3)を切り替えて学習させることができます。
2点交換、3点交換などはcube.rubiks_cube.Rubiks_3.mypermsに登録されており、それらを用いたGreedyで解を見つけることも可能です。
これらの学習データをもとに学習させるのが目的です。

## 主な機能
- AIによる自動ソルブ
- 自動学習
- キューブのサイズ変更(2x2~7x7)
- 手動でのキューブ操作
- 学習パラメータの保存・読込
- キューブの状態、評価値の推移や確率分布等の可視化

## 使用技術
- Python
- NumPy
- Tkinter
- PyTorch(一部学習・推論処理)

## 実行方法
'''bash
python main.py

## 主要な構成
- main.py
    ・アプリケーションの起点
- cube/
    ・キューブ本体、手順列操作等
- ai/
    ・ニューラルネットワーク本体、layer、loss
- managers/
    ・solve、learn、params、debugなどの管理処理
- ui/
    ・Tkinter UI
- model
    ・探索結果や学習データの構造
- core
    ・共通定数

## 探索方式
- Search2
    ・独自のGreedyベース探索です。
    　Policy確率分布に従って探索し、評価値の高いノードを優先します。
- Search3
    ・PUCTベースの探索です。
    　PolicyとValueを使って探索木を伸ばし、訪問回数の多い手を優先します。

## 補助手順
cube.rubiks_cube.Rubiks_3.mypermsには2点交換、3点交換、parity補正などの手順が登録されており、これらを用いたGreedy探索も実装されています。

## 現状の目的
このプロジェクトの主目的は
・Search2型、Search3型の探索と学習を比較、改善すること
・特定の2点交換や3点交換等に対してより短い手順を発見すること
です。

## 今後の課題
・学習データ形式の整理
・Search2/Seaerch3の学習品質改善