"""GAP R-Zone 6.5 전략 - 샘플 데이터"""
import pandas as pd
import numpy as np

def get_sample_trades() -> pd.DataFrame:
    """24건의 샘플 매매 데이터 반환"""
    data = [
        {"date":"2026-01-05","code":"005930","name":"삼성전자","market":"KOSPI","gap_rate":3.2,"target_price":72400,"stop_price":64800,"entry_price":68200,"result":"승","result_detail":"reached_20","days_to_target":5,"peak_pct":24.3,"min_low_pct":-2.1,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":True,"sector":"반도체"},
        {"date":"2026-01-08","code":"000660","name":"SK하이닉스","market":"KOSPI","gap_rate":5.8,"target_price":198000,"stop_price":172000,"entry_price":185000,"result":"승","result_detail":"reached_20","days_to_target":3,"peak_pct":28.1,"min_low_pct":-1.5,"ma_pattern":"MA5>MA20>MA60>MA40>MA120","volume_spike":True,"sector":"반도체"},
        {"date":"2026-01-12","code":"373220","name":"LG에너지솔루션","market":"KOSPI","gap_rate":4.1,"target_price":420000,"stop_price":375000,"entry_price":395000,"result":"승","result_detail":"reached_20","days_to_target":8,"peak_pct":22.5,"min_low_pct":-3.8,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"sector":"2차전지"},
        {"date":"2026-01-15","code":"247540","name":"에코프로비엠","market":"KOSDAQ","gap_rate":12.5,"target_price":285000,"stop_price":220000,"entry_price":252000,"result":"승","result_detail":"reached_20","days_to_target":4,"peak_pct":31.2,"min_low_pct":-1.9,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"2차전지"},
        {"date":"2026-01-19","code":"086520","name":"에코프로","market":"KOSDAQ","gap_rate":15.3,"target_price":130000,"stop_price":98000,"entry_price":112000,"result":"패","result_detail":"stopped","days_to_target":12,"peak_pct":8.4,"min_low_pct":-14.2,"ma_pattern":"MA5>MA20>MA60","volume_spike":True,"sector":"2차전지"},
        {"date":"2026-01-22","code":"035420","name":"NAVER","market":"KOSPI","gap_rate":2.8,"target_price":225000,"stop_price":198000,"entry_price":210000,"result":"승","result_detail":"reached_20","days_to_target":6,"peak_pct":21.7,"min_low_pct":-2.4,"ma_pattern":"MA5>MA20>MA60>MA40>MA120","volume_spike":False,"sector":"인터넷"},
        {"date":"2026-01-26","code":"035720","name":"카카오","market":"KOSPI","gap_rate":3.5,"target_price":58000,"stop_price":48500,"entry_price":52000,"result":"승","result_detail":"reached_20","days_to_target":7,"peak_pct":20.8,"min_low_pct":-4.1,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":True,"sector":"인터넷"},
        {"date":"2026-02-02","code":"006400","name":"삼성SDI","market":"KOSPI","gap_rate":6.2,"target_price":480000,"stop_price":415000,"entry_price":445000,"result":"승","result_detail":"reached_20","days_to_target":9,"peak_pct":25.6,"min_low_pct":-3.2,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"2차전지"},
        {"date":"2026-02-05","code":"028260","name":"삼성물산","market":"KOSPI","gap_rate":2.1,"target_price":145000,"stop_price":128000,"entry_price":135000,"result":"승","result_detail":"reached_20","days_to_target":11,"peak_pct":20.2,"min_low_pct":-1.8,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"sector":"지주"},
        {"date":"2026-02-09","code":"352820","name":"하이브","market":"KOSPI","gap_rate":8.7,"target_price":310000,"stop_price":262000,"entry_price":285000,"result":"패","result_detail":"stopped","days_to_target":15,"peak_pct":6.2,"min_low_pct":-12.8,"ma_pattern":"MA5>MA20>MA60","volume_spike":True,"sector":"엔터"},
        {"date":"2026-02-12","code":"263750","name":"펄어비스","market":"KOSDAQ","gap_rate":9.4,"target_price":62000,"stop_price":48500,"entry_price":54000,"result":"승","result_detail":"reached_20","days_to_target":6,"peak_pct":26.8,"min_low_pct":-2.7,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"게임"},
        {"date":"2026-02-16","code":"293490","name":"카카오게임즈","market":"KOSDAQ","gap_rate":7.1,"target_price":32000,"stop_price":25500,"entry_price":28000,"result":"승","result_detail":"reached_20","days_to_target":4,"peak_pct":23.4,"min_low_pct":-1.6,"ma_pattern":"MA5>MA20>MA60>MA40>MA120","volume_spike":False,"sector":"게임"},
        {"date":"2026-02-19","code":"068270","name":"셀트리온","market":"KOSPI","gap_rate":4.6,"target_price":215000,"stop_price":188000,"entry_price":198000,"result":"승","result_detail":"reached_80","days_to_target":42,"peak_pct":21.2,"min_low_pct":-5.8,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"sector":"바이오"},
        {"date":"2026-02-23","code":"207940","name":"삼성바이오로직스","market":"KOSPI","gap_rate":3.9,"target_price":850000,"stop_price":755000,"entry_price":795000,"result":"승","result_detail":"reached_20","days_to_target":10,"peak_pct":22.8,"min_low_pct":-3.5,"ma_pattern":"MA5>MA20>MA60>MA40>MA120","volume_spike":True,"sector":"바이오"},
        {"date":"2026-02-26","code":"377300","name":"카카오페이","market":"KOSPI","gap_rate":11.2,"target_price":52000,"stop_price":39000,"entry_price":44500,"result":"승","result_detail":"reached_20","days_to_target":3,"peak_pct":29.5,"min_low_pct":-1.2,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"핀테크"},
        {"date":"2026-03-02","code":"003670","name":"포스코퓨처엠","market":"KOSPI","gap_rate":7.8,"target_price":355000,"stop_price":295000,"entry_price":320000,"result":"패","result_detail":"stopped","days_to_target":18,"peak_pct":5.1,"min_low_pct":-11.5,"ma_pattern":"MA5>MA20>MA60","volume_spike":False,"sector":"소재"},
        {"date":"2026-03-05","code":"112040","name":"위메이드","market":"KOSDAQ","gap_rate":18.5,"target_price":78000,"stop_price":55000,"entry_price":65000,"result":"승","result_detail":"reached_20","days_to_target":2,"peak_pct":35.4,"min_low_pct":-0.8,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"게임"},
        {"date":"2026-03-08","code":"041510","name":"에스엠","market":"KOSDAQ","gap_rate":6.3,"target_price":115000,"stop_price":95000,"entry_price":102000,"result":"승","result_detail":"reached_20","days_to_target":5,"peak_pct":24.1,"min_low_pct":-2.9,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":True,"sector":"엔터"},
        {"date":"2026-03-10","code":"009150","name":"삼성전기","market":"KOSPI","gap_rate":4.4,"target_price":175000,"stop_price":152000,"entry_price":162000,"result":"승","result_detail":"reached_20","days_to_target":7,"peak_pct":21.9,"min_low_pct":-3.1,"ma_pattern":"MA5>MA20>MA60>MA40>MA120","volume_spike":False,"sector":"전자부품"},
        {"date":"2026-03-12","code":"066570","name":"LG전자","market":"KOSPI","gap_rate":2.9,"target_price":118000,"stop_price":104000,"entry_price":110000,"result":"승","result_detail":"reached_20","days_to_target":8,"peak_pct":20.5,"min_low_pct":-2.6,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"sector":"가전"},
        {"date":"2026-03-14","code":"259960","name":"크래프톤","market":"KOSPI","gap_rate":5.6,"target_price":295000,"stop_price":255000,"entry_price":272000,"result":"패","result_detail":"stopped","days_to_target":14,"peak_pct":7.8,"min_low_pct":-10.3,"ma_pattern":"MA5>MA20>MA60","volume_spike":True,"sector":"게임"},
        {"date":"2026-03-16","code":"036570","name":"엔씨소프트","market":"KOSPI","gap_rate":8.1,"target_price":245000,"stop_price":205000,"entry_price":222000,"result":"승","result_detail":"reached_20","days_to_target":6,"peak_pct":23.7,"min_low_pct":-2.3,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"게임"},
        {"date":"2026-03-17","code":"196170","name":"알테오젠","market":"KOSDAQ","gap_rate":14.2,"target_price":320000,"stop_price":250000,"entry_price":280000,"result":"승","result_detail":"reached_20","days_to_target":3,"peak_pct":26.8,"min_low_pct":-1.4,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"sector":"바이오"},
        {"date":"2026-03-17","code":"090430","name":"아모레퍼시픽","market":"KOSPI","gap_rate":3.8,"target_price":155000,"stop_price":135000,"entry_price":142000,"result":"승","result_detail":"reached_20","days_to_target":7,"peak_pct":22.1,"min_low_pct":-0.6,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"sector":"화장품"},
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_sample_equity_curve() -> pd.DataFrame:
    """30일 자산 추이 데이터"""
    dates = pd.date_range("2026-02-16", periods=30, freq="B")
    values = [45200000,45800000,46100000,45500000,46200000,47100000,47800000,
              47200000,48100000,48900000,49500000,49200000,49800000,48400000,
              47200000,47800000,48500000,49800000,50200000,50800000,51200000,
              50500000,51000000,51500000,51800000,51200000,50400000,51100000,
              51800000,52340000]
    return pd.DataFrame({"date": dates[:len(values)], "value": values})


def get_sample_positions() -> pd.DataFrame:
    """보유 종목 데이터"""
    return pd.DataFrame([
        {"name": "알테오젠", "code": "196170", "weight": 18.5, "pnl": 8.2, "amount": 9692900},
        {"name": "아모레퍼시픽", "code": "090430", "weight": 12.3, "pnl": 4.5, "amount": 6437820},
    ])


def get_sample_signals() -> pd.DataFrame:
    """활성 시그널"""
    return pd.DataFrame([
        {"code":"196170","name":"알테오젠","market":"KOSDAQ","gap_rate":14.2,"current_price":303000,"target_price":320000,"stop_price":250000,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"strength":"강"},
        {"code":"090430","name":"아모레퍼시픽","market":"KOSPI","gap_rate":3.8,"current_price":148400,"target_price":155000,"stop_price":135000,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"strength":"중"},
        {"code":"051910","name":"LG화학","market":"KOSPI","gap_rate":5.1,"current_price":388000,"target_price":415000,"stop_price":365000,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":True,"strength":"강"},
        {"code":"105560","name":"KB금융","market":"KOSPI","gap_rate":2.4,"current_price":77500,"target_price":82000,"stop_price":74000,"ma_pattern":"MA5>MA20>MA60>MA120","volume_spike":False,"strength":"약"},
        {"code":"323410","name":"카카오뱅크","market":"KOSPI","gap_rate":6.8,"current_price":34200,"target_price":38500,"stop_price":31000,"ma_pattern":"MA5>MA20>MA40>MA60>MA120","volume_spike":True,"strength":"강"},
    ])
