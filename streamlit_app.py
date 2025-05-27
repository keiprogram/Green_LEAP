import streamlit as st
import pandas as pd
import numpy as np

# アプリ設定
st.set_page_config(page_title="English Vocabulary Test", page_icon="📝")

# データ読み込み（各Partを個別に）
@st.cache_data
def load_part_data(filename):
    df = pd.read_excel(filename)
    df.columns = ["No.", "単語", "語の意味"]
    return df

# ファイル名のマッピング
part_files = {
    "Part 1": "data/part1.xlsx",
    "Part 2": "data/part2.xlsx",
    "Part 3": "data/part3.xlsx",
    "Part 4": "data/part4.xlsx",
}

# UIタイトル
st.title("English Vocabulary Test")
st.caption("アップロードされた単語帳で学ぶ英単語テストアプリ")

# サイドバー設定
selected_part = st.sidebar.selectbox("学習するパートを選択", list(part_files.keys()))
test_type = st.sidebar.radio("テスト形式を選択", ["英語→日本語", "日本語→英語"])

# データ読み込み
words_df = load_part_data(part_files[selected_part])

# 範囲指定
max_no = int(words_df["No."].max())
ranges = [(i, min(i+99, max_no)) for i in range(1, max_no+1, 100)]
range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
selected_label = st.sidebar.selectbox("出題範囲", range_labels)
selected_range = ranges[range_labels.index(selected_label)]

# 出題数選択
num_questions = st.sidebar.slider("出題数", 1, 50, 10)

# 指定範囲でフィルタ
filtered_df = words_df[(words_df["No."] >= selected_range[0]) & (words_df["No."] <= selected_range[1])]

# テスト開始ボタン
if st.sidebar.button("テスト開始"):
    st.session_state.test_started = True
    st.session_state.questions = filtered_df.sample(n=min(num_questions, len(filtered_df))).reset_index(drop=True)
    st.session_state.current = 0
    st.session_state.correct = 0
    st.session_state.wrongs = []

# 回答処理
def answer_question(opt):
    q = st.session_state.questions.iloc[st.session_state.current]
    correct = q["語の意味"] if test_type == "英語→日本語" else q["単語"]
    if opt == correct:
        st.session_state.correct += 1
    else:
        st.session_state.wrongs.append((q["No."], q["単語"], q["語の意味"]))
    st.session_state.current += 1

# テスト進行中
if st.session_state.get("test_started", False) and st.session_state.current < len(st.session_state.questions):
    q = st.session_state.questions.iloc[st.session_state.current]
    question_text = q["単語"] if test_type == "英語→日本語" else q["語の意味"]
    correct_answer = q["語の意味"] if test_type == "英語→日本語" else q["単語"]

    # 選択肢生成
    pool = filtered_df["語の意味"] if test_type == "英語→日本語" else filtered_df["単語"]
    choices = list(pool.drop_duplicates().sample(min(3, len(pool.drop_duplicates()))))
    choices.append(correct_answer)
    np.random.shuffle(choices)

    st.subheader(f"問題 {st.session_state.current+1} / {len(st.session_state.questions)}")
    st.write(question_text)

    for opt in choices:
        st.button(opt, on_click=answer_question, args=(opt,))

# テスト終了後
elif st.session_state.get("test_started", False) and st.session_state.current >= len(st.session_state.questions):
    total = len(st.session_state.questions)
    correct = st.session_state.correct
    st.success(f"テスト終了！ 正解数: {correct}/{total}")
    st.progress(correct / total)
    
    if st.session_state.wrongs:
        df_wrong = pd.DataFrame(st.session_state.wrongs, columns=["No.", "単語", "語の意味"])
        st.subheader("間違えた問題一覧")
        st.dataframe(df_wrong)
    else:
        st.write("全問正解です！おめでとうございます！")
