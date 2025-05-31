import streamlit as st
import pandas as pd
import numpy as np
import os

# アプリの設定
st.set_page_config(page_title="緑⁻プ英単語テスト", page_icon="📝")

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
    # 実際の列名を確認
    st.write("読み込んだデータの列名:", combined_df.columns.tolist())
    # 列名を標準化（仮定: Excelファイルの列名が異なる可能性を考慮）
    expected_columns = ['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group']
    if not all(col in combined_df.columns for col in expected_columns[:-1]):  # Groupは追加済みなので除外
        # 列名が異なる場合、最初の6列を想定の列名に割り当て
        if len(combined_df.columns) >= 6:
            combined_df.columns = expected_columns
        else:
            st.error("Excelファイルの列数が不足しています。必要な列: No., 単語, CEFR, 語の意味, 用例（英語）, 用例（日本語）")
            return pd.DataFrame()
    return combined_df

words_df = load_data()

if words_df.empty:
    st.stop()

# セッション状態の初期化
if 'wrong_answers_list' not in st.session_state:
    st.session_state.wrong_answers_list = []
if 'correct_answers_list' not in st.session_state:
    st.session_state.correct_answers_list = []
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'finished' not in st.session_state:
    st.session_state.finished = False

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語', '間違えた問題'], key="test_type")

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
        LEAP Basicテストアプリを試す
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# データ抽出
if test_type == "間違えた問題" and st.session_state.wrong_answers_list:
    filtered_words_df = pd.DataFrame(st.session_state.wrong_answers_list, 
                                    columns=['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group'])
else:
    filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) & 
                               (words_df['No.'] <= selected_range[1])]

# 単語数表示
st.sidebar.write(f"選択範囲の単語数: {len(filtered_words_df)}")

# テスト開始
if st.button('テストを開始する'):
    if test_type == "間違えた問題" and not st.session_state.wrong_answers_list:
        st.error("まだ間違えた問題がありません。通常のテストを行ってください。")
    elif len(filtered_words_df) == 0:
        st.error("選択した範囲に単語がありません。別の範囲を選択してください。")
    elif len(filtered_words_df) < num_questions:
        st.warning(f"選択した範囲の単語数（{len(filtered_words_df)}語）が指定した出題数（{num_questions}問）より少ないため、{len(filtered_words_df)}問でテストを開始します。")
        st.session_state.update({
            'test_started': True,
            'correct_answers': 0,
            'current_question': 0,
            'finished': False,
            'wrong_answers': [],
            'selected_questions': filtered_words_df.sample(n=len(filtered_words_df)).reset_index(drop=True),
            'total_questions': len(filtered_words_df)
        })
    else:
        st.session_state.update({
            'test_started': True,
            'correct_answers': 0,
            'current_question': 0,
            'finished': False,
            'wrong_answers': [],
            'selected_questions': filtered_words_df.sample(n=num_questions).reset_index(drop=True),
            'total_questions': num_questions
        })

# 質問更新
def update_question(answer):
    if st.session_state.current_question >= st.session_state.total_questions:
        st.session_state.finished = True
        return
    
    current_data = st.session_state.current_question_data
    correct_answer = current_data['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else current_data['単語']
    question_word = current_data['単語'] if test_type in ['英語→日本語', '間違えた問題'] else current_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
        # 正解を記録
        st.session_state.correct_answers_list.append((
            current_data['No.'], 
            current_data['単語'], 
            current_data['CEFR'], 
            current_data['語の意味'], 
            current_data['用例（英語）'], 
            current_data['用例（日本語）'], 
            current_data['Group']
        ))
        # 間違えた問題リストから削除
        if test_type == "間違えた問題":
            st.session_state.wrong_answers_list = [w for w in st.session_state.wrong_answers_list 
                                                if w[0] != current_data['No.']]
    else:
        # 間違えた問題または「わからない」を記録
        st.session_state.wrong_answers.append((
            current_data['No.'], 
            question_word, 
            correct_answer
        ))
        if (current_data['No.'], current_data['単語'], current_data['CEFR'], 
            current_data['語の意味'], current_data['用例（英語）'], 
            current_data['用例（日本語）'], current_data['Group']) not in st.session_state.wrong_answers_list:
            st.session_state.wrong_answers_list.append((
                current_data['No.'], 
                current_data['単語'], 
                current_data['CEFR'], 
                current_data['語の意味'], 
                current_data['用例（英語）'], 
                current_data['用例（日本語）'], 
                current_data['Group']
            ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        pool = st.session_state.selected_questions['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else st.session_state.selected_questions['単語']
        correct_answer = st.session_state.current_question_data['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else st.session_state.current_question_data['単語']
        
        # 選択肢生成（正解を除く最大4つの誤答）
        choices = list(pool[pool != correct_answer].drop_duplicates().sample(n=min(4, len(pool[pool != correct_answer].drop_duplicates()))))
        if correct_answer not in choices:
            choices.append(correct_answer)
        # 選択肢が4つ未満の場合、範囲内のデータから補充
        if len(choices) < 4:
            remaining_pool = pool[~pool.isin(choices)].drop_duplicates()
            if len(remaining_pool) > 0:
                additional_choices = list(remaining_pool.sample(n=min(4 - len(choices), len(remaining_pool))))
                choices.extend(additional_choices)
            # それでも足りない場合、正解済みの問題から補充
            if len(choices) < 4 and st.session_state.correct_answers_list:
                correct_df = pd.DataFrame(st.session_state.correct_answers_list, 
                                       columns=['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group'])
                correct_pool = correct_df['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else correct_df['単語']
                remaining_correct_pool = correct_pool[~correct_pool.isin(choices)].drop_duplicates()
                if len(remaining_correct_pool) > 0:
                    additional_choices = list(remaining_correct_pool.sample(n=min(4 - len(choices), len(remaining_correct_pool))))
                    choices.extend(additional_choices)
            # それでも足りない場合は警告
            if len(choices) < 4:
                st.warning("選択肢が不足しています。範囲内の単語数および正解済みの問題が少ないため、選択肢を4つに満たせませんでした。")
        # 「わからない」を追加
        choices.append("わからない")
        np.random.shuffle(choices)
        st.session_state.options = choices
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
if 'test_started' in st.session_state and st.session_state.test_started and not st.session_state.finished:
    if 'current_question_data' not in st.session_state:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[0]
        pool = st.session_state.selected_questions['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else st.session_state.selected_questions['単語']
        correct_answer = st.session_state.current_question_data['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else st.session_state.current_question_data['単語']
        choices = list(pool[pool != correct_answer].drop_duplicates().sample(n=min(4, len(pool[pool != correct_answer].drop_duplicates()))))
        if correct_answer not in choices:
            choices.append(correct_answer)
        if len(choices) < 4:
            remaining_pool = pool[~pool.isin(choices)].drop_duplicates()
            if len(remaining_pool) > 0:
                additional_choices = list(remaining_pool.sample(n=min(4 - len(choices), len(remaining_pool))))
                choices.extend(additional_choices)
            if len(choices) < 4 and st.session_state.correct_answers_list:
                correct_df = pd.DataFrame(st.session_state.correct_answers_list, 
                                       columns=['No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）', 'Group'])
                correct_pool = correct_df['語の意味'] if test_type in ['英語→日本語', '間違えた問題'] else correct_df['単語']
                remaining_correct_pool = correct_pool[~correct_pool.isin(choices)].drop_duplicates()
                if len(remaining_correct_pool) > 0:
                    additional_choices = list(remaining_correct_pool.sample(n=min(4 - len(choices), len(remaining_correct_pool))))
                    choices.extend(additional_choices)
            if len(choices) < 4:
                st.warning("選択肢が不足しています。範囲内の単語数および正解済みの問題が少ないため、選択肢を4つに満たせませんでした。")
        choices.append("わからない")
        np.random.shuffle(choices)
        st.session_state.options = choices
        st.session_state.answer = None

    st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions} (問題番号: {st.session_state.current_question_data['No.']})")
    st.subheader(f"{st.session_state.current_question_data['単語']}" if test_type in ['英語→日本語', '間違えた問題'] else f"{st.session_state.current_question_data['語の意味']}")

    progress = (st.session_state.current_question + 1) / st.session_state.total_questions
    st.progress(progress)

    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(st.session_state.options):
        st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if 'test_started' in st.session_state and st.session_state.finished:
        display_results()

# 画像表示
image_path = os.path.join("data", "English.png")
if os.path.exists(image_path):
    st.image(image_path)
else:
    st.warning("画像ファイルが見つかりません: " + image_path)