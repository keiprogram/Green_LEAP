import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="緑リープ英単語テスト", layout="wide")

# スタイル適用
st.markdown(
    """
    <style>
    body {
        background-color: #022033;
        color: #ffae4b;
    }
    .stApp {
        background-color: #022033;
        color: #ffae4b;
    }
    .css-1d391kg {
        color: #ffae4b;
    }
    .stTextInput > div > div > input {
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ファイルパス設定（Streamlit Cloudでは /mount/data）
part_files = {
    "Part 1": "/data/part1.xlsx",
    "Part 2": "/data/part2.xlsx",
    "Part 3": "/data/part3.xlsx",
    "Part 4": "/data/part4.xlsx",
}

# データ読み込み関数（必要な列のみ抽出）
@st.cache_data
def load_part_data(filename):
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        expected_cols = ["No.", "単語", "語の意味"]
        available_cols = df.columns.tolist()
        if all(col in available_cols for col in expected_cols):
            return df[expected_cols]
        else:
            st.error("必要な列（No., 単語, 語の意味）が見つかりません")
            return None
    else:
        st.error(f"ファイルが存在しません: {filename}")
        return None

# --- UI 表示 ---

st.title("🌿 緑リープ英単語テスト")

selected_part = st.selectbox("学習するパートを選択してください", list(part_files.keys()))

words_df = load_part_data(part_files[selected_part])

if words_df is not None and not words_df.empty:

    num_questions = st.slider("出題数を選んでください", min_value=1, max_value=len(words_df), value=5)
    questions = random.sample(words_df.to_dict('records'), num_questions)

    user_answers = []
    st.write("---")

    for i, q in enumerate(questions):
        st.write(f"**{i+1}. {q['語の意味']}**")
        answer = st.text_input(f"あなたの答え（No.{q['No.']}）", key=f"input_{i}")
        user_answers.append({
            "question": q['語の意味'],
            "correct": q['単語'],
            "user": answer.strip()
        })

    st.write("---")
    if st.button("採点"):
        correct_count = 0
        results = []
        for ans in user_answers:
            is_correct = ans["user"].lower() == ans["correct"].lower()
            if is_correct:
                correct_count += 1
            results.append(f"【{'〇' if is_correct else '×'}】{ans['question']} → あなたの答え: {ans['user']} / 正解: {ans['correct']}")

        st.subheader(f"✅ 正解数: {correct_count} / {num_questions}")
        for res in results:
            st.write(res)
else:
    st.warning("データが読み込めませんでした。")
