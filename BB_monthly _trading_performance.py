# bb_indicators_trade.py 에서 생성한 2024년 월별 거래 내역 파일을 불러와서 월별 수익금액/평균 거래 가격, 월별 수익률/승률, 월별 거래 횟수를 시각화

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm
import platform

# 운영체제별 폰트 설정
if platform.system() == 'Darwin':  # Mac
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows':  # Windows
    plt.rc('font', family='Malgun Gothic')
else:  # Linux
    plt.rc('font', family='NanumGothic')

# 마이너스 기호 깨짐 방지
plt.rc('axes', unicode_minus=False)

# 폰트 경로 직접 지정 (다른 방법들이 실패할 경우 사용)
# font_path = r'C:\Windows\Fonts\malgun.ttf'  # Windows
# font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # Linux
# font = fm.FontProperties(fname=font_path).get_name()
# plt.rc('font', family=font)

def analyze_monthly_performance(csv_files):
    monthly_data = []
    
    for file in csv_files:
        df = pd.read_csv(file)
        month = pd.to_datetime(df['진입일자']).dt.strftime('%Y-%m').iloc[0]
        
        total_profit = df['수익금액'].sum()
        total_return = df['수익률'].sum()
        avg_entry_price = df['진입가격'].mean()
        trade_count = len(df)
        win_count = len(df[df['수익금액'] > 0])
        
        monthly_data.append({
            'month': month,
            'total_profit': total_profit,
            'total_return': total_return,
            'avg_price': avg_entry_price,
            'trade_count': trade_count,
            'win_rate': win_count / trade_count * 100
        })
    
    return pd.DataFrame(monthly_data)
# 월별 수익금액/평균 거래 가격, 월별 수익률/승률, 월별 거래 횟수를 시각화
def plot_monthly_performance(df):
    plt.style.use('seaborn')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 18))
    
    # 1. 수익금액과 평균 거래가격
    ax1_2 = ax1.twinx()
    
    bars = ax1.bar(df['month'], df['total_profit'] / 1000000, color='skyblue', alpha=0.7)
    ax1.set_ylabel('월별 수익금액 (백만원)', color='skyblue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='skyblue', labelsize=10)
    
    # 수익금액 레이블 추가
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}M',
                ha='center', va='bottom')
    
    line = ax1_2.plot(df['month'], df['avg_price'] / 1000000, color='red', linewidth=2, marker='o')
    ax1_2.set_ylabel('평균 거래가격 (백만원)', color='red', fontsize=12)
    ax1_2.tick_params(axis='y', labelcolor='red', labelsize=10)
    
    # 2. 수익률과 승률
    ax2_2 = ax2.twinx()
    
    bars2 = ax2.bar(df['month'], df['total_return'], color='lightgreen', alpha=0.7)
    ax2.set_ylabel('월별 수익률 합계 (%)', color='green', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='green', labelsize=10)
    
    # 수익률 레이블 추가
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    line2 = ax2_2.plot(df['month'], df['win_rate'], color='purple', linewidth=2, marker='o')
    ax2_2.set_ylabel('승률 (%)', color='purple', fontsize=12)
    ax2_2.tick_params(axis='y', labelcolor='purple', labelsize=10)
    
    # 3. 거래 횟수
    bars3 = ax3.bar(df['month'], df['trade_count'], color='orange', alpha=0.7)
    ax3.set_ylabel('월별 거래 횟수', fontsize=12)
    ax3.tick_params(labelsize=10)
    
    # 거래 횟수 레이블 추가
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # 공통 스타일링
    for ax in [ax1, ax2, ax3]:
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    # 제목 추가
    ax1.set_title('월별 수익금액과 평균 거래가격', pad=20, fontsize=14)
    ax2.set_title('월별 수익률과 승률', pad=20, fontsize=14)
    ax3.set_title('월별 거래 횟수', pad=20, fontsize=14)
    
    plt.tight_layout(pad=3.0)
    plt.show()

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
files = [f'monthly_bb_trade/2024{month}01_trade_history_bb.csv' for month in months]
df = analyze_monthly_performance(files)
plot_monthly_performance(df)
