import streamlit as st
import pandas as pd
import numpy as np

# アプリの設定
st.set_page_config(page_title="緑リープ英単語テスト", page_icon='English Logo.png')

# カスタムCSSでUIを改善
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

# Excelデータを読み込む関数（緑リープ用）
@st.cache_data
def load_data():
    # リポジトリ内のPart 1〜4ファイルを自動検出
    import glob, os
    pattern = os.path.join("**", "見出語・用例リスト(Part *.xlsx)")
    file_paths = glob.glob(pattern, recursive=True)
    if not file_paths:
        st.error("Excelファイルが見つかりませんでした。ファイル名を確認してください。")
        return pd.DataFrame(columns=["Group","No.","単語","CEFR","語の意味","用例（英語）","用例（日本語）"])
    dfs = []
    for fp in sorted(file_paths):
        df = pd.read_excel(fp)
        df = df.iloc[:, :7]
        df.columns = ["Group","No.","単語","CEFR","語の意味","用例（英語）","用例（日本語）"][:df.shape[1]]
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    # No.列を数値化
    combined_df['No.'] = pd.to_numeric(combined_df['No.'], errors='coerce')
    combined_df = combined_df.dropna(subset=['No.'])
    combined_df['No.'] = combined_df['No.'].astype(int)
    return combined_df
    # 'No.'列を数値化して不正データを除去
    combined_df['No.'] = pd.to_numeric(combined_df['No.'], errors='coerce')
    combined_df = combined_df.dropna(subset=['No.'])
    combined_df['No.'] = combined_df['No.'].astype(int)
    return combined_df

# データ読み込み
words_df = load_data()

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

# 単語範囲選択（No.1〜No.100形式）
max_no = int(words_df['No.'].max())
ranges = [(i + 1, min(i + 100, max_no)) for i in range(0, max_no, 100)]
range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
selected_range_label = st.sidebar.selectbox("単語範囲を選択", range_labels)
selected_range = ranges[range_labels.index(selected_range_label)]

# 出題問題数の選択
num_questions = st.sidebar.slider("出題問題数を選択", 1, 50, 10)

# サイドバーにリンクボタンを追加
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p>こちらのアプリもお試しください</p>
        <a href="https://sisutann-f5r6e9hvuz3ubw5umd6m4i.streamlit.app/" target="_blank" 
        style="background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        アプリを試す
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# 選択した条件に基づくデータを抽出
filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) &
                             (words_df['No.'] <= selected_range[1])]

st.image("English.png")
st.title("緑リープ 英単語テスト")
st.text("緑リープの単語帳からクイズ形式で出題します。")

# テスト開始ボタン
if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
    })

    # ランダムに問題を選択
    selected_questions = filtered_words_df.sample(min(num_questions, len(filtered_words_df))).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    # 初回の選択肢を生成
    if test_type == '英語→日本語':
        options = list(selected_questions['語の意味'].sample(min(3, len(selected_questions))))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(selected_questions['単語'].sample(min(3, len(selected_questions))))
        options.append(st.session_state.current_question_data['単語'])

    np.random.shuffle(options)
    st.session_state.options = options

# 質問を進める関数
def update_question(answer):
    data = st.session_state.current_question_data
    if test_type == '英語→日本語':
        correct_answer = data['語の意味']
        question_word = data['単語']
    else:
        correct_answer = data['単語']
        question_word = data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append((
            data['No.'], question_word, correct_answer
        ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        next_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        st.session_state.current_question_data = next_data
        if test_type == '英語→日本語':
            opts = list(st.session_state.selected_questions['語の意味'].sample(min(3, len(st.session_state.selected_questions))))
            opts.append(next_data['語の意味'])
        else:
            opts = list(st.session_state.selected_questions['単語'].sample(min(3, len(st.session_state.selected_questions))))
            opts.append(next_data['単語'])
        np.random.shuffle(opts)
        st.session_state.options = opts
    else:
        st.session_state.finished = True

# 結果を表示する関数
def display_results():
    correct = st.session_state.correct_answers
    total = st.session_state.total_questions
    accuracy = correct / total

    st.write(f"テスト終了！正解数: {correct}/{total}")
    st.progress(accuracy)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct)
    with col2:
        st.metric("不正解数", total - correct)
    st.markdown(f"正答率: {accuracy:.0%}")

    if st.session_state.wrong_answers:
        df_wrong = pd.DataFrame(st.session_state.wrong_answers, columns=["No.", "問題", "正答"])
        st.subheader("間違えた問題一覧")
        st.markdown(df_wrong.to_html(classes='results-table', index=False), unsafe_allow_html=True)

# 問題表示ロジック
if st.session_state.get('test_started') and not st.session_state.finished:
    data = st.session_state.current_question_data
    prompt = data['単語'] if test_type == '英語→日本語' else data['語の意味']
    st.subheader(f"問題 {st.session_state.current_question+1}/{st.session_state.total_questions} (No.{data['No.']})")
    st.write(prompt)
    for idx, opt in enumerate(st.session_state.options):
        if st.button(opt, key=f"btn_{idx}"):
            update_question(opt)

elif st.session_state.get('test_started') and st.session_state.finished:
    display_results()
