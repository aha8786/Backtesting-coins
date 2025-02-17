# bb_indicators_trade.py 에서 생성한 2024년 월별 성과 시각화

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

def load_monthly_data():
    # 현재 파일의 디렉토리 경로 가져오기
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 모든 월의 파일 목록
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    all_data = []
    
    for month in months:
        filename = f'2024{month}01_trade_history_bb.csv'
        full_path = os.path.join(base_path, filename)
        
        try:
            df = pd.read_csv(full_path)
            # 날짜 컬럼을 datetime으로 변환
            df['진입일자'] = pd.to_datetime(df['진입일자'])
            df['종료일자'] = pd.to_datetime(df['종료일자'])
            all_data.append(df)
            print(f"{filename} 로드 완료")
        except FileNotFoundError:
            print(f"{filename} 파일을 찾을 수 없습니다. 경로: {full_path}")
            continue
    
    # 데이터가 있는지 확인
    if not all_data:
        raise ValueError("로드된 데이터가 없습니다. 파일 경로를 확인해주세요.")
    
    # 모든 데이터를 하나의 데이터프레임으로 합치기
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

def analyze_monthly_performance(df):
    """월별 성과 분석"""
    # 월별 데이터 그룹화
    df['월'] = df['진입일자'].dt.strftime('%Y-%m')
    monthly_stats = df.groupby('월').agg({
        '수익금액': ['count', 'sum', 'mean', 'std'],
        '수익률': ['mean', 'std', lambda x: (x > 0).mean() * 100]  # 승률 추가
    }).round(2)
    
    # 컬럼명 변경
    monthly_stats.columns = [
        '거래횟수', '총수익', '평균수익', '수익표준편차',
        '평균수익률', '수익률표준편차', '승률'
    ]
    
    # 추가 지표 계산
    monthly_stats['샤프비율'] = monthly_stats['평균수익률'] / monthly_stats['수익률표준편차']
    
    return monthly_stats

def plot_monthly_performance(stats):
    """월별 성과 시각화"""
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정
    plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 월별 총수익
    axes[0, 0].grid(True, zorder=0)  # grid를 먼저 그리고 zorder를 0으로 설정
    axes[0, 0].bar(range(len(stats.index)), stats['총수익'], color='skyblue', zorder=3)  # bar의 zorder를 더 높게 설정
    axes[0, 0].set_title('월별 총수익률')
    axes[0, 0].set_xticks(range(len(stats.index)))
    axes[0, 0].set_xticklabels(stats.index, rotation=45)
    
    # 2. 월별 거래횟수
    axes[0, 1].grid(True, zorder=0)
    axes[0, 1].bar(range(len(stats.index)), stats['거래횟수'], color='lightgreen', zorder=3)
    axes[0, 1].set_title('월별 거래횟수')
    axes[0, 1].set_xticks(range(len(stats.index)))
    axes[0, 1].set_xticklabels(stats.index, rotation=45)
    
    # 3. 월별 승률
    axes[1, 0].grid(True, zorder=0)
    axes[1, 0].bar(range(len(stats.index)), stats['승률'], color='salmon', zorder=3)
    axes[1, 0].set_title('월별 승률 (%)')
    axes[1, 0].set_xticks(range(len(stats.index)))
    axes[1, 0].set_xticklabels(stats.index, rotation=45)
    
    # 4. 월별 샤프비율
    axes[1, 1].grid(True, zorder=0)
    axes[1, 1].bar(range(len(stats.index)), stats['샤프비율'], color='purple', zorder=3)
    axes[1, 1].set_title('월별 샤프비율')
    axes[1, 1].set_xticks(range(len(stats.index)))
    axes[1, 1].set_xticklabels(stats.index, rotation=45)
    
    plt.tight_layout()
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 현재 스크립트의 디렉토리에 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, f'monthly_performance_{timestamp}.png')
    
    # 이미지 저장 (높은 DPI로 저장하여 품질 향상)
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    print(f"\n그래프가 저장되었습니다: {image_path}")
    
    plt.show()

def print_monthly_summary(stats):
    """월별 성과 요약 출력"""
    print("\n=== 월별 거래 성과 요약 ===")
    print("\n1. 기본 통계")
    print(stats.round(2))
    
    print("\n2. 전체 성과 요약")
    print(f"총 거래횟수: {stats['거래횟수'].sum():,}회")
    print(f"총 수익: {stats['총수익'].sum():,.0f}원")
    print(f"평균 월간 수익: {stats['총수익'].mean():,.0f}원")
    print(f"평균 승률: {stats['승률'].mean():.2f}%")
    print(f"평균 샤프비율: {stats['샤프비율'].mean():.2f}")
    
    best_month = stats['총수익'].idxmax()
    worst_month = stats['총수익'].idxmin()
    print(f"\n최고 수익 월: {best_month} ({stats.loc[best_month, '총수익']:,.0f}원)")
    print(f"최저 수익 월: {worst_month} ({stats.loc[worst_month, '총수익']:,.0f}원)")

def main():
    try:
        # 현재 파일의 디렉토리 경로 가져오기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 데이터 로드
        print("데이터 로딩 중...")
        print(f"작업 디렉토리: {current_dir}")
        combined_data = load_monthly_data()
        
        # 월별 성과 분석
        print("\n월별 성과 분석 중...")
        monthly_stats = analyze_monthly_performance(combined_data)
        
        # 결과 시각화 및 저장
        print("\n그래프 생성 및 저장 중...")
        plot_monthly_performance(monthly_stats)
        
        # 결과 출력
        print_monthly_summary(monthly_stats)
        
        # 결과를 CSV로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(current_dir, f'monthly_performance_summary_{timestamp}.csv')
        monthly_stats.to_csv(output_path, encoding='utf-8-sig')
        print(f"\n월별 성과 분석 결과가 {output_path}에 저장되었습니다.")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print("프로그램을 종료합니다.")

if __name__ == "__main__":
    # font_path = "C:/Windows/Fonts/malgun.ttf" 
    
    # try:
    #     font_name = font_manager.FontProperties(fname=font_path).get_name()
    #     rc('font', family=font_name)
    #     print("font 설정 완료")
    # except Exception as e:
    #     print(f"폰트 설정 오류: {e}")
    #     print("기본 폰트로 설정합니다.")    

    main()