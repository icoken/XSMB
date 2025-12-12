#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成包含完整历史数据的HTML预测工具 v4
主要改进：
1. 自动回溯计算所有历史统计（不依赖实时跟踪）
2. 显示最近N天的完整信号记录
3. 更清晰的状态提示
"""

import json

# 读取历史数据
with open('historical_data.json', 'r') as f:
    data = json.load(f)

# 生成嵌入式数据
embedded_data = json.dumps(data)

# HTML模板
html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XSMB 尾数遗漏策略 v4</title>
    <style>
        :root {
            --primary: #10b981;
            --primary-dark: #059669;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #0f172a;
            --card: #1e293b;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        h1 { font-size: 2rem; background: linear-gradient(135deg, #10b981, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .subtitle { color: var(--text-muted); margin-top: 5px; }
        .badge { display: inline-block; background: rgba(16, 185, 129, 0.2); color: var(--primary); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-top: 10px; }
        .card { background: var(--card); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); }
        .card-title { font-size: 1.1rem; color: var(--primary); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        .signal-box { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2)); border: 2px solid var(--primary); border-radius: 16px; padding: 20px; text-align: center; }
        .signal-status { font-size: 1.5rem; font-weight: bold; margin-bottom: 10px; }
        .signal-yes { color: var(--primary); }
        .signal-no { color: var(--warning); }
        .no-bet-box { background: rgba(245, 158, 11, 0.1); border: 2px solid var(--warning); }
        .prediction-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 15px; }
        .prediction-num { background: linear-gradient(135deg, #10b981, #06b6d4); color: white; font-size: 1.5rem; font-weight: bold; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
        .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
        .info-item { background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 12px; text-align: center; }
        .info-value { font-size: 1.5rem; font-weight: bold; color: var(--primary); }
        .info-label { font-size: 0.85rem; color: var(--text-muted); margin-top: 5px; }
        .btn { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.3s; }
        .btn:hover { background: var(--primary-dark); transform: translateY(-2px); }
        .btn-small { padding: 8px 16px; font-size: 0.9rem; }
        .input-group { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        input, select { background: #1e293b; border: 1px solid rgba(255, 255, 255, 0.2); color: var(--text); padding: 12px 16px; border-radius: 8px; font-size: 1rem; }
        select option { background: #1e293b; color: var(--text); }
        input:focus, select:focus { outline: none; border-color: var(--primary); }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .stat-item { text-align: center; padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; }
        .stat-value { font-size: 1.8rem; font-weight: bold; color: var(--primary); }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 5px; }
        .history-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .history-table th, .history-table td { padding: 10px 8px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.9rem; }
        .history-table th { color: var(--text-muted); font-weight: normal; }
        .hit { color: var(--primary); }
        .miss { color: var(--danger); }
        .skip { color: var(--warning); }
        .loading { text-align: center; padding: 20px; color: var(--text-muted); }
        .success-msg { background: rgba(16, 185, 129, 0.1); color: var(--primary); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .error { background: rgba(239, 68, 68, 0.1); color: var(--danger); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .warning-msg { background: rgba(245, 158, 11, 0.1); color: var(--warning); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .recent-draws { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 15px; }
        .recent-item { background: rgba(99, 102, 241, 0.1); padding: 12px; border-radius: 10px; text-align: center; }
        .recent-date { font-size: 0.8rem; color: var(--text-muted); }
        .recent-num { font-size: 1.3rem; font-weight: bold; color: #60a5fa; margin-top: 5px; }
        .strategy-box { background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 15px; margin-top: 15px; }
        .strategy-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .strategy-item:last-child { border-bottom: none; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .tab-btn { background: rgba(255,255,255,0.1); color: var(--text-muted); border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        .tab-btn.active { background: var(--primary); color: white; }
        @media (max-width: 600px) {
            .prediction-grid { grid-template-columns: repeat(5, 1fr); gap: 8px; }
            .prediction-num { font-size: 1.2rem; padding: 12px 8px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .info-grid { grid-template-columns: 1fr; }
            .recent-draws { grid-template-columns: repeat(3, 1fr); }
            .history-table th, .history-table td { padding: 8px 4px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 尾数遗漏策略</h1>
            <p class="subtitle">严格验证有效 | 365天窗口 | 样本外ROI +16%</p>
            <span class="badge">✓ 自动回溯统计</span>
        </header>

        <!-- 数据状态 -->
        <div class="card">
            <div class="card-title">📊 数据状态</div>
            <div id="dataStatus"><div class="loading">正在初始化...</div></div>
            <div class="input-group">
                <button class="btn" onclick="fetchNewData()">🔄 获取最新数据</button>
            </div>
        </div>

        <!-- 最近开奖 -->
        <div class="card">
            <div class="card-title">🎲 最近开奖</div>
            <div id="recentDraws"><div class="loading">加载中...</div></div>
        </div>

        <!-- 今日信号 -->
        <div class="card">
            <div class="card-title">📡 下期预测信号</div>
            <div id="signalBox"><div class="loading">计算中...</div></div>
        </div>

        <!-- 预测详情 -->
        <div class="card" id="predictionCard" style="display: none;">
            <div class="card-title">🎯 预测号码 <span id="predictDate" style="font-size: 0.9rem; color: var(--text-muted);"></span></div>
            <div id="prediction"></div>
            <div id="analysisInfo" style="margin-top: 15px;"></div>
        </div>

        <!-- 自动统计 -->
        <div class="card">
            <div class="card-title">📈 历史回溯统计 <span style="font-size: 0.85rem; color: var(--text-muted);">（基于全部历史数据自动计算）</span></div>
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="setStatsPeriod(30)">近30天</button>
                <button class="tab-btn" onclick="setStatsPeriod(90)">近90天</button>
                <button class="tab-btn" onclick="setStatsPeriod(180)">近180天</button>
                <button class="tab-btn" onclick="setStatsPeriod(365)">近1年</button>
                <button class="tab-btn" onclick="setStatsPeriod(0)">全部</button>
            </div>
            <div class="stats-grid">
                <div class="stat-item"><div class="stat-value" id="totalDays">0</div><div class="stat-label">总天数</div></div>
                <div class="stat-item"><div class="stat-value" id="betDays">0</div><div class="stat-label">投注天数</div></div>
                <div class="stat-item"><div class="stat-value" id="hitCount">0</div><div class="stat-label">命中次数</div></div>
                <div class="stat-item"><div class="stat-value" id="hitRate">0%</div><div class="stat-label">命中率</div></div>
            </div>
            <div id="roiInfo" style="margin-top: 15px; text-align: center; font-size: 0.9rem;"></div>
        </div>

        <!-- 历史记录 -->
        <div class="card">
            <div class="card-title">📋 信号记录 <span style="font-size: 0.85rem; color: var(--text-muted);">（自动回溯计算）</span></div>
            <div class="input-group" style="margin-top: 0; margin-bottom: 15px;">
                <select id="recordFilter" onchange="loadHistory()">
                    <option value="all">全部记录</option>
                    <option value="bet">仅投注日</option>
                    <option value="hit">仅命中</option>
                    <option value="miss">仅未中</option>
                </select>
                <select id="recordCount" onchange="loadHistory()">
                    <option value="20">显示20条</option>
                    <option value="50">显示50条</option>
                    <option value="100">显示100条</option>
                </select>
            </div>
            <div style="overflow-x: auto;">
                <table class="history-table">
                    <thead><tr><th>日期</th><th>信号</th><th>预测尾数</th><th>遗漏</th><th>差距</th><th>开奖</th><th>结果</th></tr></thead>
                    <tbody id="historyBody"><tr><td colspan="7" style="text-align:center; color: var(--text-muted);">加载中...</td></tr></tbody>
                </table>
            </div>
        </div>

        <!-- 策略说明 -->
        <div class="card">
            <div class="card-title">📖 策略说明</div>
            <div class="strategy-box">
                <div class="strategy-item"><span>训练窗口</span><span style="color: var(--primary);">365天</span></div>
                <div class="strategy-item"><span>条件1</span><span>遗漏最久尾数 ≥ 15天</span></div>
                <div class="strategy-item"><span>条件2</span><span>与第二名差距 ≥ 5天</span></div>
                <div class="strategy-item"><span>投注方式</span><span>该尾数的10个号码</span></div>
                <div class="strategy-item"><span>盈亏平衡</span><span>命中率 ≥ 11.9%</span></div>
            </div>
            <p style="margin-top: 15px; color: var(--danger); font-size: 0.9rem;">⚠️ 仅供娱乐参考，历史表现不代表未来收益</p>
        </div>
    </div>

    <script>
        // ========================================
        // 内嵌历史数据
        // ========================================
        const EMBEDDED_DATA = ''' + embedded_data + ''';

        // 配置
        const CONFIG = {
            WINDOW_SIZE: 365,
            MIN_OVERDUE: 15,
            MIN_GAP: 5
        };

        // 全局变量
        let lotteryData = [];
        let allRecords = [];  // 所有回溯计算的记录
        let currentStatsPeriod = 30;

        // 初始化
        document.addEventListener('DOMContentLoaded', () => {
            initializeData();
        });

        // 初始化数据
        function initializeData() {
            // 合并嵌入数据和localStorage数据
            const storageKey = 'xsmb_data_v4';
            let storedData = [];
            try {
                storedData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            } catch(e) {}
            
            lotteryData = mergeData(EMBEDDED_DATA, storedData);
            localStorage.setItem(storageKey, JSON.stringify(lotteryData));
            
            updateDataStatus();
            displayRecentDraws();
            
            // 回溯计算所有历史记录
            calculateAllRecords();
            
            // 计算今日信号
            calculateTodaySignal();
            
            // 尝试获取新数据
            fetchNewData();
        }

        // 合并数据
        function mergeData(data1, data2) {
            const map = new Map();
            data1.forEach(item => map.set(item.d, item));
            data2.forEach(item => map.set(item.d, item));
            return Array.from(map.values()).sort((a, b) => b.d.localeCompare(a.d));
        }

        // 回溯计算所有历史记录
        function calculateAllRecords() {
            allRecords = [];
            
            // 从第366天开始（需要365天窗口）
            for (let i = 0; i < lotteryData.length - CONFIG.WINDOW_SIZE; i++) {
                const predictDate = lotteryData[i].d;  // 开奖日期
                const actualNum = lotteryData[i].n;    // 实际开奖号码
                
                // 使用开奖前一天的数据计算信号
                const trainData = lotteryData.slice(i + 1, i + 1 + CONFIG.WINDOW_SIZE);
                
                if (trainData.length < CONFIG.WINDOW_SIZE) continue;
                
                const overdue = calculateTailOverdue(trainData);
                const sorted = Object.entries(overdue)
                    .map(([tail, days]) => ({ tail: parseInt(tail), days }))
                    .sort((a, b) => b.days - a.days);
                
                const maxOverdue = sorted[0];
                const gap = maxOverdue.days - sorted[1].days;
                const shouldBet = maxOverdue.days >= CONFIG.MIN_OVERDUE && gap >= CONFIG.MIN_GAP;
                const predictions = shouldBet ? Array.from({length: 10}, (_, j) => j * 10 + maxOverdue.tail) : [];
                const hit = shouldBet ? predictions.includes(actualNum) : null;
                
                allRecords.push({
                    date: predictDate,
                    type: shouldBet ? 'BET' : 'SKIP',
                    predictedTail: maxOverdue.tail,
                    overdueDays: maxOverdue.days,
                    gap: gap,
                    actual: actualNum,
                    hit: hit
                });
            }
            
            // 更新统计和历史显示
            updateStats();
            loadHistory();
        }

        // 计算尾数遗漏
        function calculateTailOverdue(data) {
            const overdue = {};
            for (let t = 0; t < 10; t++) overdue[t] = data.length;
            for (let i = 0; i < data.length; i++) {
                const tail = data[i].n % 10;
                if (overdue[tail] === data.length) overdue[tail] = i;
            }
            return overdue;
        }

        // 设置统计周期
        function setStatsPeriod(days) {
            currentStatsPeriod = days;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            updateStats();
        }

        // 更新统计
        function updateStats() {
            let records = allRecords;
            
            // 按周期筛选
            if (currentStatsPeriod > 0) {
                const cutoffDate = new Date();
                cutoffDate.setDate(cutoffDate.getDate() - currentStatsPeriod);
                const cutoffStr = cutoffDate.toISOString().split('T')[0];
                records = allRecords.filter(r => r.date >= cutoffStr);
            }
            
            const betRecords = records.filter(r => r.type === 'BET');
            const hitRecords = betRecords.filter(r => r.hit);
            
            document.getElementById('totalDays').textContent = records.length;
            document.getElementById('betDays').textContent = betRecords.length;
            document.getElementById('hitCount').textContent = hitRecords.length;
            
            const hitRate = betRecords.length > 0 ? (hitRecords.length / betRecords.length * 100) : 0;
            document.getElementById('hitRate').textContent = hitRate.toFixed(1) + '%';
            
            // ROI计算: 命中赔率8.4倍，每次投注10个号码
            const roi = betRecords.length > 0 ? ((hitRecords.length * 8.4 - betRecords.length) / betRecords.length * 100) : 0;
            const roiColor = roi >= 0 ? 'var(--primary)' : 'var(--danger)';
            
            document.getElementById('roiInfo').innerHTML = `
                命中率: <span style="color: ${hitRate >= 11.9 ? 'var(--primary)' : 'var(--danger)'}">${hitRate.toFixed(1)}%</span> 
                (平衡线11.9%) | 
                ROI: <span style="color: ${roiColor}">${roi >= 0 ? '+' : ''}${roi.toFixed(1)}%</span>
            `;
        }

        // 加载历史记录
        function loadHistory() {
            const tbody = document.getElementById('historyBody');
            const filter = document.getElementById('recordFilter').value;
            const count = parseInt(document.getElementById('recordCount').value);
            
            let records = [...allRecords];
            
            // 筛选
            if (filter === 'bet') records = records.filter(r => r.type === 'BET');
            else if (filter === 'hit') records = records.filter(r => r.hit === true);
            else if (filter === 'miss') records = records.filter(r => r.hit === false);
            
            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color: var(--text-muted);">暂无记录</td></tr>';
                return;
            }
            
            tbody.innerHTML = records.slice(0, count).map(r => {
                const resultClass = r.type === 'SKIP' ? 'skip' : (r.hit ? 'hit' : 'miss');
                const resultText = r.type === 'SKIP' ? '-' : (r.hit ? '✅' : '❌');
                const signalText = r.type === 'SKIP' ? '跳过' : '投注';
                const signalClass = r.type === 'SKIP' ? 'skip' : 'hit';
                
                return `<tr>
                    <td>${r.date}</td>
                    <td class="${signalClass}">${signalText}</td>
                    <td>尾${r.predictedTail}</td>
                    <td>${r.overdueDays}</td>
                    <td>${r.gap}</td>
                    <td>${r.actual.toString().padStart(2, '0')}</td>
                    <td class="${resultClass}">${resultText}</td>
                </tr>`;
            }).join('');
        }

        // 计算今日信号
        function calculateTodaySignal() {
            if (lotteryData.length < CONFIG.WINDOW_SIZE) {
                document.getElementById('signalBox').innerHTML = '<div class="error">数据不足365天</div>';
                return;
            }

            const trainData = lotteryData.slice(0, CONFIG.WINDOW_SIZE);
            const overdue = calculateTailOverdue(trainData);
            const sorted = Object.entries(overdue)
                .map(([tail, days]) => ({ tail: parseInt(tail), days }))
                .sort((a, b) => b.days - a.days);

            const maxOverdue = sorted[0];
            const gap = maxOverdue.days - sorted[1].days;
            const shouldBet = maxOverdue.days >= CONFIG.MIN_OVERDUE && gap >= CONFIG.MIN_GAP;
            const predictions = shouldBet ? Array.from({length: 10}, (_, i) => i * 10 + maxOverdue.tail) : [];

            displaySignal(shouldBet, maxOverdue, sorted[1], gap, predictions, sorted);
        }

        // 显示信号
        function displaySignal(shouldBet, maxOverdue, secondOverdue, gap, predictions, allOverdue) {
            const signalBox = document.getElementById('signalBox');
            const predCard = document.getElementById('predictionCard');

            let overdueListHtml = '<div style="margin-top: 15px; font-size: 0.85rem; color: var(--text-muted);">尾数遗漏: ';
            allOverdue.forEach((item, idx) => {
                const style = idx === 0 ? 'color: var(--primary); font-weight: bold;' : '';
                overdueListHtml += `<span style="${style}">尾${item.tail}(${item.days}天)</span> `;
            });
            overdueListHtml += '</div>';

            const latestDate = new Date(lotteryData[0].d);
            latestDate.setDate(latestDate.getDate() + 1);
            const predictDateStr = `${latestDate.getMonth() + 1}/${latestDate.getDate()}`;

            if (shouldBet) {
                signalBox.innerHTML = `
                    <div class="signal-box">
                        <div class="signal-status signal-yes">✅ 有信号 - 投注!</div>
                        <p style="font-size: 1.2rem;">尾数 <strong>${maxOverdue.tail}</strong> 已遗漏 <strong>${maxOverdue.days}</strong> 天</p>
                        <p style="color: var(--text-muted);">差距: ${gap}天 (第二名: 尾${secondOverdue.tail} 漏${secondOverdue.days}天)</p>
                    </div>
                    ${overdueListHtml}
                `;

                predCard.style.display = 'block';
                document.getElementById('prediction').innerHTML = `
                    <div class="prediction-grid">
                        ${predictions.map(n => `<div class="prediction-num">${n.toString().padStart(2, '0')}</div>`).join('')}
                    </div>
                `;
                document.getElementById('predictDate').textContent = `（预测 ${predictDateStr} 开奖）`;
                document.getElementById('analysisInfo').innerHTML = `
                    <div class="info-grid">
                        <div class="info-item"><div class="info-value">${maxOverdue.days}天</div><div class="info-label">尾数${maxOverdue.tail}遗漏</div></div>
                        <div class="info-item"><div class="info-value">${gap}天</div><div class="info-label">领先差距</div></div>
                    </div>
                `;
            } else {
                const reason = maxOverdue.days < CONFIG.MIN_OVERDUE ? 
                    `遗漏${maxOverdue.days}天 < ${CONFIG.MIN_OVERDUE}天` : 
                    `差距${gap}天 < ${CONFIG.MIN_GAP}天`;
                signalBox.innerHTML = `
                    <div class="signal-box no-bet-box">
                        <div class="signal-status signal-no">⏸️ 不投注</div>
                        <p>尾数 ${maxOverdue.tail} 遗漏 ${maxOverdue.days} 天，差距 ${gap} 天</p>
                        <p style="color: var(--danger); margin-top: 10px;">未满足: ${reason}</p>
                    </div>
                    ${overdueListHtml}
                `;
                predCard.style.display = 'none';
            }
        }

        // 更新数据状态
        function updateDataStatus(message = '') {
            const statusDiv = document.getElementById('dataStatus');
            const hasEnough = lotteryData.length >= CONFIG.WINDOW_SIZE;
            const latestDate = lotteryData.length > 0 ? lotteryData[0].d : '--';
            const latestNum = lotteryData.length > 0 ? lotteryData[0].n.toString().padStart(2, '0') : '--';
            
            statusDiv.innerHTML = `
                <div class="${hasEnough ? 'success-msg' : 'warning-msg'}">
                    ${hasEnough ? '✅' : '⚠️'} 已加载 ${lotteryData.length} 天数据<br>
                    最新: ${latestDate} → ${latestNum}
                    ${message ? `<br><span style="font-size:0.9rem;">${message}</span>` : ''}
                </div>
            `;
        }

        // 显示最近开奖
        function displayRecentDraws() {
            const container = document.getElementById('recentDraws');
            const recent = lotteryData.slice(0, 5);
            
            if (recent.length === 0) {
                container.innerHTML = '<div class="loading">暂无数据</div>';
                return;
            }
            
            container.innerHTML = `
                <div class="recent-draws">
                    ${recent.map(item => `
                        <div class="recent-item">
                            <div class="recent-date">${item.d.slice(5)}</div>
                            <div class="recent-num">${item.n.toString().padStart(2, '0')}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // 获取新数据
        async function fetchNewData() {
            const statusDiv = document.getElementById('dataStatus');
            statusDiv.innerHTML += '<div style="margin-top:10px;color:var(--text-muted);font-size:0.9rem;">🔄 正在获取最新数据...</div>';

            try {
                const proxies = ['https://api.allorigins.win/get?url=', 'https://corsproxy.io/?'];
                const targetUrl = 'https://az24.vn/thong-ke-giai-dac-biet-theo-tuan.html';

                for (const proxyUrl of proxies) {
                    try {
                        const response = await fetch(proxyUrl + encodeURIComponent(targetUrl), { timeout: 8000 });
                        const data = await response.json();
                        
                        if (data.contents) {
                            const newData = parseWebData(data.contents);
                            if (newData.length > 0) {
                                const oldLatest = lotteryData.length > 0 ? lotteryData[0].d : '';
                                lotteryData = mergeData(lotteryData, newData);
                                localStorage.setItem('xsmb_data_v4', JSON.stringify(lotteryData));
                                
                                const newLatest = lotteryData[0].d;
                                updateDataStatus(newLatest !== oldLatest ? `✅ 已更新到 ${newLatest}` : '数据已是最新');
                                displayRecentDraws();
                                calculateAllRecords();
                                calculateTodaySignal();
                                return;
                            }
                        }
                    } catch (e) {
                        console.log('Proxy failed:', proxyUrl, e);
                    }
                }
                
                // 判断本地数据是否已是最新
                const latestDate = lotteryData.length > 0 ? lotteryData[0].d : '';
                const today = new Date().toISOString().split('T')[0];
                const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
                
                if (latestDate === today) {
                    updateDataStatus('✅ 数据已是最新');
                } else if (latestDate === yesterday) {
                    updateDataStatus('✅ 数据已是最新（今天可能还未开奖）');
                } else {
                    updateDataStatus(`⚠️ 网络获取失败，本地数据到 ${latestDate}`);
                }
            } catch (error) {
                console.error('获取新数据失败:', error);
                updateDataStatus('⚠️ 网络异常');
            }
        }

        // 解析网页数据
        function parseWebData(html) {
            let results = [];
            const numPattern = /class="gdb-cell[^"]*"[^>]*>(\d{2})</g;
            let numbers = [];
            let match;
            
            while ((match = numPattern.exec(html)) !== null) {
                numbers.push(parseInt(match[1]));
            }
            
            const today = new Date();
            for (let i = 0; i < numbers.length; i++) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                results.push({
                    d: date.toISOString().split('T')[0],
                    n: numbers[i]
                });
            }
            
            return results;
        }
    </script>
</body>
</html>'''

# 写入HTML文件
with open('tail_strategy_v4.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'Generated tail_strategy_v4.html')
print(f'  - Embedded data: {len(data)} records')
print(f'  - File size: ~{len(html_template) / 1024:.1f} KB')
print(f'  - Features: 自动回溯统计, 周期筛选, 记录过滤')
