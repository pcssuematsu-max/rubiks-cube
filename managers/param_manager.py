"""Parameter save/load helpers."""

from __future__ import annotations

import os
import pickle
import numpy as np

class ParamManager:
    """AIパラメータの保存・読込と、対象AI indexの解釈を担当する。"""

    def __init__(self, frame):
        self.frame = frame

    def selected_indices(self, text):
        """カンマ区切りの入力文字列から、有効なAI indexだけを重複なしで取り出す。"""
        if text.strip() == '':
            return []
        indices = []
        for part in text.split(','):
            index = self._parse_index(part)
            if index is not None and index not in indices:
                indices.append(index)
        return indices

    def _parse_index(self, text):
        """1つの文字列をAI indexとして解釈し、範囲外や不正値ならNoneを返す。"""
        text = text.strip()
        if text == '':
            return None
        try:
            index = int(text)
        except ValueError:
            return None
        if 0 <= index < self.frame.AInum:
            return index
        return None

    def load(self, index, keylis = None):
        """指定AIのパラメータ・optimizer状態をAIdatasから読み込む。"""
        ai = self.frame.AIs[index]
        data_dir = self._data_dir(index)
        for key in self._target_keys(ai, keylis):
            self._load_param_set(ai, data_dir, key)
        self._after_load(ai)

    def save(self, index, keylis = None):
        """指定AIのパラメータ・optimizer状態をAIdatasへ保存する。"""
        ai = self.frame.AIs[index]
        data_dir = self._data_dir(index)
        for key in self._target_keys(ai, keylis):
            self._save_param_set(ai, data_dir, key)

    def load_all(self, keylis = None):
        """全AIのパラメータを順番に読み込む。"""
        for index in range(self.frame.AInum):
            self.load(index, keylis = keylis)

    def save_all(self, keylis = None):
        """全AIのパラメータを順番に保存する。"""
        for index in range(self.frame.AInum):
            self.save(index, keylis = keylis)

    def load_selected(self, text, keylis = None):
        """入力欄で指定されたAI indexだけを読み込む。"""
        for index in self.selected_indices(text):
            self.load(index, keylis = keylis)

    def save_selected(self, text, keylis = None):
        """入力欄で指定されたAI indexだけを保存する。"""
        for index in self.selected_indices(text):
            self.save(index, keylis = keylis)

    def _data_dir(self, index):
        """AI indexに対応する保存ディレクトリ名を作る。"""
        return './AIdatas' + str(index)

    def _target_keys(self, ai, keylis):
        """除外リストに含まれないパラメータkeyだけを列挙する。"""
        skipped_keys = set([] if keylis is None else keylis)
        return [key for key in ai.params.keys() if key not in skipped_keys]

    def _load_param_set(self, ai, data_dir, key):
        """1つのkeyについて、重み・v・hを読み込む。"""
        ai.params[key][:] = np.load(os.path.join(data_dir,key + '.npy'))
        ai.v[key][:] = np.load(os.path.join(data_dir,key + '_v.npy'))
        ai.h[key][:] = np.load(os.path.join(data_dir,key + '_h.npy'))

    def _save_param_set(self, ai, data_dir, key):
        """1つのkeyについて、重み・v・hを保存する。"""
        np.save(os.path.join(data_dir,key + '.npy'),ai.params[key])
        np.save(os.path.join(data_dir,key + '_v.npy'),ai.v[key])
        np.save(os.path.join(data_dir,key + '_h.npy'),ai.h[key])

    def _after_load(self, ai):
        """読込後に完成状態の評価値と推論キャッシュを更新する。"""
        ai.set_perfect_val()
        ai.mark_params_dirty()


