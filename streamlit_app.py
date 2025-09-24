import streamlit as st
import pandas as pd
import numpy as np
import os

# --- アプリ設定 ---
st.set_page_config(page_title="緑ープ英単語テスト")

# カスタムCSS
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        color: #333;
    }
    .choices-container button {
        background-color: #6c757d;
        color: white;
        border: 2px solid #6c757d;
        margin: 5px;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    .choices-container button:hover {
        background-color: #495057;
        color: white;
    }
    .test-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .results-table {
        margin: 20px auto;
        border-collapse: collapse;
        width: 100%;
        background-color: white;
        color: #333;
    }
    .results-table th {
        background-color: #6c757d;
        color: white;
        padding: 10px;
    }
    .results-table td {
        border: 1px solid #6c757d;
        padding: 8px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #6c757d;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- データ読み込み ---
@st.cache_data
def load_data():
    data_dir = "data"
    file_names = ["part1.xlsx", "part2.xlsx", "part3.xlsx", "part4.xlsx"]
    file_paths = [os.path.join(data_dir, file_name) for file_name in file_names]
    dataframes = []

    for i, file_path in enumerate(file_paths, 1):
        if not os.path.exists(file_path):
            st.error(f"ファイルが見つかりません: {file_path}")
            return pd.DataFrame()
        df = pd.read_excel(file_path)
        df['Group'] = f'Part{i}'
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.columns = ['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group']
    return combined_df

words_df = load_data()
if words_df.empty:
    st.stop()

# --- サイドバー（テスト設定） ---
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

mode = st.sidebar.radio("出題範囲の選び方", ["100単語ごと", "自由指定"], key="range_mode")
if mode == "100単語ごと":
    ranges = [(i + 1, i + 100) for i in range(0, 1600, 100)]
    range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
    selected_range_label = st.sidebar.selectbox("単語範囲を選択", range_labels)
    selected_range = ranges[range_labels.index(selected_range_label)]
else:
    min_no = int(words_df['No.'].min())
    max_no = int(words_df['No.'].max())
    st.sidebar.write(f"範囲を指定してください（{min_no}〜{max_no}）")
    start_no = st.sidebar.number_input("開始No.", min_value=min_no, max_value=max_no, value=min_no)
    end_no = st.sidebar.number_input("終了No.", min_value=min_no, max_value=max_no, value=min_no+99)
    if start_no > end_no:
        st.sidebar.error("開始No.は終了No.以下にしてください")
    selected_range = (start_no, end_no)

# 選択範囲抽出
filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) &
                             (words_df['No.'] <= selected_range[1])].reset_index(drop=True)

max_questions = len(filtered_words_df)
if max_questions == 0:
    st.warning("選択範囲に単語が存在しません")
    st.stop()

num_questions = st.sidebar.slider("出題問題数を選択", 1, min(50, max_questions), 10)

# --- 出題履歴リセットボタン ---
if st.sidebar.button("出題履歴をリセット"):
    st.session_state["asked_questions"] = set()
    st.success("出題履歴をリセットしました！")

# リンクボタン
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p>こちらのアプリもお試しください</p>
        <a href="https://leap-test-app.streamlit.app/" target="_blank" 
        style="background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        LEAP Basicテストアプリ
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# 画像表示
image_path = os.path.join("data", "English.png")
if os.path.exists(image_path):
    st.image(image_path)
else:
    st.warning("画像ファイルが見つかりません: " + image_path)

st.title("緑ープ英単語テスト")
st.text("英単語テストができます")

# --- テスト開始処理 ---
def start_test():
    st.session_state['test_started'] = True
    st.session_state['correct_answers'] = 0
    st.session_state['current_question'] = 0
    st.session_state['finished'] = False
    st.session_state['wrong_answers'] = []
    st.session_state['test_type'] = test_type

    if "asked_questions" not in st.session_state:
        st.session_state["asked_questions"] = set()

    # No. 重複除去
    unique_df = filtered_words_df.drop_duplicates(subset="No.")

    # 出題済みを除外
    available_df = unique_df[~unique_df["No."].isin(st.session_state["asked_questions"])]

    if available_df.empty:
        st.warning("これ以上新しい問題はありません。範囲を変えてください。")
        st.stop()

    n_select = min(num_questions, len(available_df))
    chosen_idx = np.random.choice(available_df.index, size=n_select, replace=False)
    selected_questions = available_df.loc[chosen_idx].reset_index(drop=True)

    # 出題履歴に追加
    st.session_state["asked_questions"].update(selected_questions["No."].tolist())

    st.session_state['selected_questions'] = selected_questions
    st.session_state['total_questions'] = len(selected_questions)

    # 選択肢作成
    options_list = []
    for _, row in selected_questions.iterrows():
        if test_type == '英語→日本語':
            pool = filtered_words_df[
                (filtered_words_df['No.'] != row['No.']) &
                (filtered_words_df['語の意味'] != row['語の意味'])
            ]['語の意味'].dropna().unique().tolist()
            n_dummies = min(3, len(pool))
            dummies = list(np.random.choice(pool, size=n_dummies, replace=False)) if n_dummies > 0 else []
            options = dummies + [row['語の意味']]
        else:
            pool = filtered_words_df[
                (filtered_words_df['No.'] != row['No.']) &
                (filtered_words_df['単語'] != row['単語'])
            ]['単語'].dropna().unique().tolist()
            n_dummies = min(3, len(pool))
            dummies = list(np.random.choice(pool, size=n_dummies, replace=False)) if n_dummies > 0 else []
            options = dummies + [row['単語']]

        np.random.shuffle(options)
        options_list.append(options)

    st.session_state['options_list'] = options_list

# テスト開始ボタン
if st.button('テストを開始する'):
    start_test()

# --- 回答処理 ---
def submit_answer():
    idx = st.session_state['current_question']
    sel_key = f"radio_{idx}"
    selected = st.session_state.get(sel_key, None)
    if selected is None:
        st.warning("選択肢を選んでください（必ず1つ選択してください）")
        return

    row = st.session_state['selected_questions'].iloc[idx]
    if st.session_state['test_type'] == '英語→日本語':
        correct_answer = row['語の意味']
        question_word = row['単語']
    else:
        correct_answer = row['単語']
        question_word = row['語の意味']

    if selected == correct_answer:
        st.session_state['correct_answers'] += 1
    else:
        st.session_state['wrong_answers'].append((row['No.'], question_word, correct_answer))

    st.session_state['current_question'] += 1
    if st.session_state['current_question'] >= st.session_state['total_questions']:
        st.session_state['finished'] = True

# --- 結果表示 ---
def display_results():
    correct_answers = st.session_state['correct_answers']
    total_questions = st.session_state['total_questions']
    accuracy = correct_answers / total_questions if total_questions > 0 else 0

    st.write(f"テスト終了！正解数: {correct_answers}/{total_questions}")
    st.progress(accuracy)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct_answers)
    with col2:
        st.metric("不正解数", total_questions - correct_answers)

    st.write(f"正答率: {accuracy:.0%}")

    if st.session_state['wrong_answers']:
        df_wrong_answers = pd.DataFrame(st.session_state['wrong_answers'], columns=["問題番号", "単語", "正答"])
        st.markdown(df_wrong_answers.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.write("間違えた問題はありません。")

# --- 問題表示 ---
if st.session_state.get('test_started') and not st.session_state.get('finished'):
    idx = st.session_state['current_question']
    total = st.session_state['total_questions']
    row = st.session_state['selected_questions'].iloc[idx]

    if st.session_state['test_type'] == '英語→日本語':
        question_text = row['単語']
    else:
        question_text = row['語の意味']

    st.subheader(f"問題 {idx + 1} / {total} (問題番号: {row['No.']})")
    st.subheader(question_text)

    progress = (idx + 1) / total
    st.progress(progress)

    options = st.session_state['options_list'][idx]
    st.radio("選択肢から1つ選んでください", options, key=f"radio_{idx}")

    if st.button("回答する", key=f"submit_{idx}"):
        submit_answer()

elif st.session_state.get('test_started') and st.session_state.get('finished'):
    display_results()
else:
    st.write("範囲と出題数を選んで「テストを開始する」を押してください。")
