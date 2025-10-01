import streamlit as st
import pandas as pd
import numpy as np
import os
import random

# アプリの設定
st.set_page_config(page_title="緑リープ英単語テスト")

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

# Excelデータを読み込む関数
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

# --- サイドバー設定 ---
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

# 出題範囲のモード選択
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

# 出題範囲抽出
filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) &
                             (words_df['No.'] <= selected_range[1])]

max_questions = len(filtered_words_df)
if max_questions == 0:
    st.warning("選択範囲に単語が存在しません")
    st.stop()

num_questions = st.sidebar.slider("出題問題数を選択", 1, min(50, max_questions), 10)

# 画像表示
image_path = os.path.join("data", "English.png")
if os.path.exists(image_path):
    st.image(image_path)

st.title("緑リープ英単語テスト")
st.text("英単語テストができます")

# -------------------------
# 問題サンプリング
# -------------------------
def start_test():
    selected_questions = filtered_words_df.sample(min(num_questions, len(filtered_words_df))).reset_index(drop=True)

    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'test_type': test_type
    })

# 選択肢を作成（正解＋ランダムダミー）
def make_options(correct_answer, all_choices):
    other_choices = [c for c in all_choices if c != correct_answer]
    options = random.sample(other_choices, min(3, len(other_choices)))
    options.append(correct_answer)
    random.shuffle(options)
    return options

# 問題更新
def update_question(answer):
    q_data = st.session_state.current_question_data
    if st.session_state.test_type == '英語→日本語':
        correct_answer = q_data['語の意味']
        question_word = q_data['単語']
    else:
        correct_answer = q_data['単語']
        question_word = q_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append((q_data['No.'], question_word, correct_answer))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
    else:
        st.session_state.finished = True

# 結果表示
def display_results():
    correct = st.session_state.correct_answers
    total = st.session_state.total_questions
    accuracy = correct / total if total > 0 else 0

    st.success(f"テスト終了！ {correct}/{total} 正解")
    st.progress(accuracy)

    st.write("正解数と不正解数")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct)
    with col2:
        st.metric("不正解数", total - correct)

    st.write(f"正答率: {accuracy:.0%}")

    if st.session_state.wrong_answers:
        df_wrong = pd.DataFrame(st.session_state.wrong_answers, columns=["問題番号", "問題", "正解"])
        st.markdown(df_wrong.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.balloons()
        st.success("間違えた問題はありません！")

# -------------------------
# UI制御
# -------------------------
if st.button('テストを開始する'):
    start_test()
    st.session_state.current_question_data = st.session_state.selected_questions.iloc[0]

if 'test_started' in st.session_state and not st.session_state.finished:
    q_idx = st.session_state.current_question
    q_data = st.session_state.current_question_data
    st.subheader(f"問題 {q_idx+1} / {st.session_state.total_questions} (No.{q_data['No.']})")

    if st.session_state.test_type == '英語→日本語':
        st.subheader(q_data['単語'])
        correct_answer = q_data['語の意味']
        all_choices = st.session_state.selected_questions['語の意味'].tolist()
    else:
        st.subheader(q_data['語の意味'])
        correct_answer = q_data['単語']
        all_choices = st.session_state.selected_questions['単語'].tolist()

    options = make_options(correct_answer, all_choices)
    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(options):
        st.button(option, key=f"button_{q_idx}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)

    st.progress((q_idx+1) / st.session_state.total_questions)

elif 'test_started' in st.session_state and st.session_state.finished:
    display_results()