import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="緑リープ英単語テスト", layout="centered")

# カスタムCSS
st.markdown("""
    <style>
        body { background-color: #e9f5f2; }
        .main { color: #2c3e50; font-family: 'Arial'; }
        .stButton>button {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        .stRadio>div>label {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 緑リープ英単語テスト")

# Excelファイル読み込み
def load_data():
    files = [
        "data/見出語・用例リスト(Part 1).xlsx",
        "data/見出語・用例リスト(Part 2).xlsx",
        "data/見出語・用例リスト(Part 3).xlsx",
        "data/見出語・用例リスト(Part 4).xlsx"
    ]
    df_all = pd.concat([pd.read_excel(f) for f in files], ignore_index=True)
    df_all = df_all.rename(columns=lambda x: x.strip())  # 列名の余計な空白を削除
    return df_all

df = load_data()

# 出題範囲選択
start = st.number_input("開始No.", min_value=1, max_value=int(df["No."].max()), value=1)
end = st.number_input("終了No.", min_value=int(start), max_value=int(df["No."].max()), value=int(start)+9)

# モード選択
mode = st.radio("出題モードを選んでください", ("英語 → 日本語", "日本語 → 英語"))

# 出題データ抽出
quiz_df = df[(df["No."] >= start) & (df["No."] <= end)].reset_index(drop=True)

if st.button("テストを開始！"):
    score = 0
    wrong_answers = []

    for i in range(len(quiz_df)):
        row = quiz_df.iloc[i]

        if mode == "英語 → 日本語":
            question = row["単語"]
            answer = row["語の意味"]
            choices = df["語の意味"].dropna().sample(3).tolist()
        else:
            question = row["語の意味"]
            answer = row["単語"]
            choices = df["単語"].dropna().sample(3).tolist()

        if answer not in choices:
            choices.append(answer)
        random.shuffle(choices)

        st.markdown(f"### Q{i+1}: {question}")
        user_answer = st.radio("選択肢:", choices, key=i)

        if user_answer == answer:
            st.success("正解！")
            score += 1
        else:
            st.error(f"不正解… 正解は: {answer}")
            wrong_answers.append((question, answer))

        st.markdown("---")

    st.markdown(f"## 🎉 あなたのスコア: {score} / {len(quiz_df)}")

    if wrong_answers:
        st.markdown("### ❌ 間違えた問題一覧")
        for q, a in wrong_answers:
            st.markdown(f"- **{q}** → {a}")
