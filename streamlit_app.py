import streamlit as st
import pandas as pd
import numpy as np
import os

# アプリの設定
st.set_page_config(page_title="Enhanced Basic Vocabulary Test")  # page_iconは必要に応じて追加

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
        df['Group'] = f'Part{i}'  # Group列を追加
        dataframes.append(df)
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.columns = ['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group']
    return combined_df

words_df = load_data()

if words_df.empty:
    st.stop()

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

# 単語範囲選択（No.1〜No.1600、100単語単位）
ranges = [(i + 1, i + 100) for i in range(0, 1600, 100)]
range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
selected_range_label = st.sidebar.selectbox("単語範囲を選択", range_labels)
selected_range = ranges[range_labels.index(selected_range_label)]

# 出題問題数の選択
num_questions = st.sidebar.slider("出題問題数を選択", 1, 50, 10)

# リンクボタン
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p>こちらのアプリもお試しください</p>
        <a href="https://leap-test-app.streamlit.app/" target="_blank" 
        style="background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        アプリを試す
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# データ抽出
filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) &
                             (words_df['No.'] <= selected_range[1])]

# 画像表示（必要に応じて有効化）
# st.image("English.png")
st.title("英単語テスト")
st.text("英単語テストができます")

# テスト開始
if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
    })

    selected_questions = filtered_words_df.sample(min(num_questions, len(filtered_words_df))).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    if test_type == '英語→日本語':
        options = list(selected_questions['語の意味'].sample(min(3, len(selected_questions))))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(selected_questions['単語'].sample(min(3, len(selected_questions))))
        options.append(st.session_state.current_question_data['単語'])

    np.random.shuffle(options)
    st.session_state.options = options
    st.session_state.answer = None

# 質問更新
def update_question(answer):
    if test_type == '英語→日本語':
        correct_answer = st.session_state.current_question_data['語の意味']
        question_word = st.session_state.current_question_data['単語']
    else:
        correct_answer = st.session_state.current_question_data['単語']
        question_word = st.session_state.current_question_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append((
            st.session_state.current_question_data['No.'],
            question_word,
            correct_answer
        ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        if test_type == '英語→日本語':
            options = list(st.session_state.selected_questions['語の意味'].sample(min(3, len(st.session_state.selected_questions))))
            options.append(st.session_state.current_question_data['語の意味'])
        else:
            options = list(st.session_state.selected_questions['単語'].sample(min(3, len(st.session_state.selected_questions))))
            options.append(st.session_state.current_question_data['単語'])
        np.random.shuffle(options)
        st.session_state.options = options
        st.session_state.answer = None
    else:
        st.session_state.finished = True

# 結果表示
def display_results():
    correct_answers = st.session_state.correct_answers
    total_questions = st.session_state.total_questions
    accuracy = correct_answers / total_questions if total_questions > 0 else 0

    st.write(f"テスト終了！正解数: {correct_answers}/{total_questions}")
    st.progress(accuracy)

    st.write("正解数と不正解数")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct_answers)
    with col2:
        st.metric("不正解数", total_questions - correct_answers)

    st.write(f"正答率: {accuracy:.0%}")

    if st.session_state.wrong_answers:
        df_wrong_answers = pd.DataFrame(st.session_state.wrong_answers, columns=["問題番号", "単語", "語の意味"])
        st.markdown(df_wrong_answers.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.write("間違えた問題はありません。")

# 問題表示
if 'test_started' in st.session_state and not st.session_state.finished:
    st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions} (問題番号: {st.session_state.current_question_data['No.']})")
    st.subheader(f"{st.session_state.current_question_data['単語']}" if test_type == '英語→日本語' else f"{st.session_state.current_question_data['語の意味']}")

    progress = (st.session_state.current_question + 1) / st.session_state.total_questions
    st.progress(progress)

    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(st.session_state.options):
        st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if 'test_started' in st.session_state and st.session_state.finished:
        display_results()