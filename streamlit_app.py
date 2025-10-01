import pandas as pd
import random
import streamlit as st
import time

# -----------------------------
# 初期化
# -----------------------------
if "test_started" not in st.session_state:
    st.session_state.test_started = False
    st.session_state.question_index = 0
    st.session_state.questions = []
    st.session_state.incorrect_answers = []
    st.session_state.test_type = ""
    st.session_state.last_answer_correct = None
    st.session_state.last_correct_answer = ""


# -----------------------------
# テスト開始関数
# -----------------------------
def start_test(start_num, end_num, num_questions, test_type, df):
    test_data = df[(df["number"] >= start_num) & (df["number"] <= end_num)]

    if test_data.empty or num_questions > len(test_data):
        st.error("範囲や出題数が不正です。")
        return

    questions = test_data.sample(n=num_questions).to_dict("records")

    # ✅ 値を1つずつ代入
    st.session_state.test_started = True
    st.session_state.question_index = 0
    st.session_state.questions = questions
    st.session_state.incorrect_answers = []
    st.session_state.test_type = test_type
    st.session_state.last_answer_correct = None
    st.session_state.last_correct_answer = ""


# -----------------------------
# 問題を表示する関数
# -----------------------------
def display_question():
    q_index = st.session_state.question_index
    questions = st.session_state.questions
    direction = st.session_state.test_type

    current_question = questions[q_index]

    if direction == "英→日":
        st.markdown(f"### 問題 {q_index + 1}: {current_question['word']}")
        correct_answer = current_question["meaning"]
        other_choices = [q["meaning"] for q in st.session_state.questions if q["meaning"] != correct_answer]
    else:  # 日→英
        st.markdown(f"### 問題 {q_index + 1}: {current_question['meaning']}")
        correct_answer = current_question["word"]
        other_choices = [q["word"] for q in st.session_state.questions if q["word"] != correct_answer]

    # 選択肢作成
    choices = [correct_answer]
    num_other_choices = min(3, len(other_choices))
    if num_other_choices > 0:
        choices.extend(random.sample(other_choices, num_other_choices))
    random.shuffle(choices)

    # 前回の判定結果を表示
    if st.session_state.last_answer_correct is not None:
        if st.session_state.last_answer_correct:
            st.success("正解！🎉")
        else:
            st.error(f"不正解… 正解は **{st.session_state.last_correct_answer}** です。")
        time.sleep(0.7)
        st.session_state.question_index += 1
        st.session_state.last_answer_correct = None
        st.rerun()

    # 回答ボタン
    for choice in choices:
        if st.button(choice, use_container_width=True, key=f"btn_{q_index}_{choice}"):
            check_answer(choice, correct_answer, current_question)


# -----------------------------
# 回答チェック
# -----------------------------
def check_answer(user_answer, correct_answer, current_question):
    if user_answer == correct_answer:
        st.session_state.last_answer_correct = True
    else:
        st.session_state.last_answer_correct = False
        st.session_state.incorrect_answers.append({
            "word": current_question["word"],
            "correct_meaning": current_question["meaning"]
        })
    st.session_state.last_correct_answer = correct_answer
    st.rerun()


# -----------------------------
# メイン
# -----------------------------
def main():
    st.title("緑-プ版 英単語テストアプリ")

    uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = ["number", "word", "part_of_speech", "meaning"]
            st.session_state.df = df
            st.success("ファイル読み込み完了！")
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")
            return

        if not st.session_state.test_started:
            st.subheader("テスト設定")
            start_num = st.number_input("開始番号", min_value=int(df["number"].min()), max_value=int(df["number"].max()), value=int(df["number"].min()))
            end_num = st.number_input("終了番号", min_value=int(df["number"].min()), max_value=int(df["number"].max()), value=int(df["number"].max()))
            num_questions = st.number_input("出題数", min_value=1, max_value=len(df), value=5)
            test_type = st.radio("出題形式", ("英→日", "日→英"))

            if st.button("テスト開始"):
                start_test(start_num, end_num, num_questions, test_type, df)

        else:
            if st.session_state.question_index < len(st.session_state.questions):
                display_question()
            else:
                st.subheader("✅ テスト終了 ✅")
                if st.session_state.incorrect_answers:
                    st.write("### 間違えた問題")
                    for wrong in st.session_state.incorrect_answers:
                        st.write(f"- 単語: **{wrong['word']}**, 正解: **{wrong['correct_meaning']}**")
                else:
                    st.balloons()
                    st.success("全問正解！すごい！")

                if st.button("もう一度テストする"):
                    st.session_state.test_started = False
                    st.rerun()


if __name__ == "__main__":
    main()