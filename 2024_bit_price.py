# 2024 월별 비트코인 가격 시각화

import pandas as pd
import matplotlib.pyplot as plt
import platform
import matplotlib.font_manager as fm

# 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':  # Mac
    plt.rc('font', family='AppleGothic')
else:  # Linux
    plt.rc('font', family='NanumGothic')
    
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def analyze_monthly_trades():
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    monthly_results = []
    
    for month in months:
        try:
            filename = f'monthly_bb_trade/2024{month}01_trade_history_bb.csv'
            df = pd.read_csv(filename)
            
            if len(df) > 0:
                total_profit = df['수익금액'].sum()
                monthly_return = df['수익률'].sum()  # 단순 합산으로 변경
                
                monthly_results.append({
                    'Month': f'2024-{month}',
                    '총 수익금': total_profit,
                    '월별 수익률': monthly_return
                })
        except Exception as e:
            print(f"{month}월 처리 중 오류 발생: {str(e)}")
            continue
    
    return pd.DataFrame(monthly_results)

def plot_monthly_analysis(df):
    if df.empty:
        print("표시할 데이터가 없습니다")
        return
        
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # 수익금액 막대 그래프 (왼쪽 y축)
    bars = ax1.bar(df['Month'], df['총 수익금'], color='#3498db', alpha=0.7, label='총 수익금')
    ax1.set_xlabel('월')
    ax1.set_ylabel('총 수익금 (원)', color='#2980b9')
    ax1.tick_params(axis='y', labelcolor='#2980b9')
    
    # 수익금액 레이블 추가
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom', color='#2980b9')
    
    # 두 번째 y축 생성
    ax2 = ax1.twinx()
    
    # 수익률 선 그래프 (오른쪽 y축)
    line1 = ax2.plot(df['Month'], df['월별 수익률'], color='#e74c3c', marker='o',
                     label='월별 수익률', linewidth=3)
    
    # 수익률 레이블 추가
    for i, v in enumerate(df['월별 수익률']):
        ax2.text(i, v, f'{v:.1f}%', 
                ha='center', va='bottom', color='#c0392b')
    
    ax2.set_ylabel('수익률 (%)', color='#c0392b')
    ax2.tick_params(axis='y', labelcolor='#c0392b')
    
    # 범례 통합
    lines = [bars] + line1
    labels = ['총 수익금', '월별 수익률']
    ax1.legend(lines, labels, loc='upper left', framealpha=0.9)
    
    # 그리드 추가
    ax1.grid(True, alpha=0.2)
    
    # x축 레이블 회전
    plt.xticks(rotation=45)
    
    plt.title('2024년 월별 트레이딩 분석', pad=20, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 월별 통계 출력
    print("\n월별 통계:")
    print(df.to_string(index=False))
    
    plt.show()

def get_monthly_btc_prices():
    # 2024년 각 월 25일의 비트코인 가격 데이터
    monthly_prices = {
        '1월': 57403000,  # 2024-01-25
        '2월': 78189000,  # 2024-02-25
        '3월': 96530000,  # 2024-03-25
        '4월': 93439000,  # 2024-04-25
        '5월': 96368000,  # 2024-05-25
        '6월': 86100000,  # 2024-06-25
        '7월': 94870000,  # 2024-07-25
        '8월': 85716000,  # 2024-08-25
        '9월': 79804000,  # 2024-09-25
        '10월': 93593000,  # 2024-10-25
        '11월': 137879000,  # 2024-11-25
        '12월': 144132000  # 2024-12-25
    }
    
    df = pd.DataFrame(list(monthly_prices.items()), columns=['월', '가격'])
    return df

def plot_monthly_btc_prices(df):
    plt.figure(figsize=(15, 8))
    
    # 막대 그래프
    bars = plt.bar(df['월'], df['가격'], color='skyblue', alpha=0.6)
    
    # 선 그래프 추가
    plt.plot(df['월'], df['가격'], color='red', marker='o', linewidth=2)
    
    # 가격 레이블 추가
    for i, price in enumerate(df['가격']):
        plt.text(i, price, f'{price:,}원', 
                ha='center', va='bottom')
    
    plt.title('2024년 월별 비트코인 가격 (25일 기준)')
    plt.xlabel('월')
    plt.ylabel('가격 (억원)')
    

    # x축 레이블 회전
    plt.xticks(rotation=45)
    
    # 그리드 추가
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 데이터 출력
    print("\n2024년 월별 비트코인 가격 (25일 기준):")
    print(df.to_string(index=False))
    
    plt.show()

if __name__ == "__main__":
    df = analyze_monthly_trades()
    plot_monthly_analysis(df)
    df = get_monthly_btc_prices()
    plot_monthly_btc_prices(df)
