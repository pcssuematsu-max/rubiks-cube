"""Learning orchestration helpers."""

from __future__ import annotations

class LearnManager:
    """FrameからAI学習の実行順序とSearch2/Search3の呼び分けを切り出す。"""

    def __init__(self, frame):
        self.frame = frame

    def learn_all(self):
        """登録されている全AIを学習する。"""
        self.learn_indices(range(self.frame.AInum))

    def learn_indices(self, indices):
        """指定されたAI index群だけを順番に学習する。"""
        for index in indices:
            if self.should_learn(index):
                result = self.learn_one(index)
                self.log_result(index,result)

    def should_learn(self, index):
        """指定AIを学習対象にするか判定する。現状は既存条件をそのまま維持する。"""
        return len(self.frame.AIs[index].indices) >= 0

    def learn_one(self, index):
        """1つのAIを学習し、学習後処理を行って結果を返す。"""
        ai = self.frame.AIs[index]
        result = self.run_learning(index,ai)
        self.after_learning(ai)
        return result

    def run_learning(self, index, ai):
        """AIのsearch_modeに応じてSearch2型またはSearch3型の学習を呼び分ける。"""
        if self.uses_search2_learning(ai):
            return ai.learn(
                transformation = self.transformation_for(index),
                flip_inside = self.flip_inside_for(index),
            )

        return ai.learn_search3(
            transformation = self.transformation_for(index),
            flip_inside = self.flip_inside_for(index),
        )

    def uses_search2_learning(self, ai):
        """このAIがSearch2型の学習を使うか判定する。"""
        return ai.search_mode == 'search2'

    def transformation_for(self, index):
        """指定AIに対応するキューブ変換indexを返す。"""
        return self.frame.transform_idx[index]

    def flip_inside_for(self, index):
        """指定AIに対応する内側反転フラグを返す。"""
        return self.frame.flip_inside_idx[index]

    def after_learning(self, ai):
        """学習後に完成状態の評価値を再計算する。"""
        ai.set_perfect_val()

    def log_result(self, index, result):
        """学習結果を標準出力へ表示する。"""
        print(index,result)


