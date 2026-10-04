// Site-wide settings: the single source of truth for pages, categories, menus, breadcrumbs, titles and cards.
// Keep this file strict JSON after the "self.SITE =" part (double quotes, no comments, no trailing commas),
// because tools/build.py reads it. After editing, run:  python3 tools/build.py
// "soon": true marks a placeholder (開發中): it shows a greyed card and has no link.
self.SITE = {
  "siteName": "Brian工具箱",
  "appName": "Brian 投資工具箱",
  "studio": "Brian工作室",
  "description": "整理一些自己在投資與生活上會用到的小工具：台股交易損益、目標價、加權平均成本、定期定額複利試算。",
  "baseUrl": "https://brianhuang1998-art.github.io/stock_analysis/",
  "repo": "brianhuang1998-art/stock_analysis",
  "themeColor": "#0f2233",
  "home": {
    "title": "首頁",
    "href": "home_page.html",
    "keywords": "home 回首頁"
  },
  "categories": [
    {
      "title": "試算工具",
      "href": "tools.html",
      "icon": "🛠",
      "keywords": "損益 手續費 證交稅",
      "description": "即時計算台股交易的手續費、證交稅與損益兩平點。",
      "homeDesc": "ETF、個股交易損益、目標%數與加權平均成本法試算。",
      "homeCta": "前往試算工具 →",
      "tools": [
        {
          "title": "ETF 試算",
          "href": "etf_calculator.html",
          "icon": "ETF",
          "desc": "依 ETF 類型（股票型／債券型／主動式）自動帶入證交稅率，計算損益與兩平點。",
          "keywords": "etf 債券 股票型 主動式 損益 兩平"
        },
        {
          "title": "個股試算",
          "href": "stock_calculator.html",
          "icon": "個股",
          "desc": "一般交易稅率 0.3%、現股當沖 0.15%，計算個股買賣的淨損益與兩平點。",
          "keywords": "個股 當沖 損益 兩平"
        },
        {
          "title": "目標%數試算",
          "href": "target_price_calculator.html",
          "icon": "%",
          "desc": "輸入價格，即時算出漲跌 1%～30% 各百分比對應的目標價。",
          "keywords": "目標價 漲跌幅 升降單位 掛單"
        },
        {
          "title": "加權平均成本法試算",
          "href": "avg_cost_calculator.html",
          "icon": "⚖️",
          "desc": "分批買進時自動算出加權平均成本、損益兩平價與目前損益。",
          "keywords": "均價 攤平 分批 平均成本"
        }
      ]
    },
    {
      "title": "交易與部位管理",
      "href": "trading_position.html",
      "icon": "📊",
      "keywords": "部位 停損 再平衡",
      "description": "幫助控制部位大小與交易紀律的試算工具。",
      "homeDesc": "定期定額複利、部位大小、停損停利與再平衡等試算工具。",
      "homeCta": "前往工具列表 →",
      "tools": [
        {
          "title": "定期定額複利試算",
          "href": "dca_calculator.html",
          "icon": "📈",
          "desc": "輸入本金、每月扣款金額與預期年化報酬率，算出N年後累積資產與總報酬。",
          "keywords": "dca 複利 存股 每月扣款 年化報酬"
        },
        {
          "title": "部位大小計算機",
          "icon": "🎯",
          "desc": "輸入可承受虧損金額與停損點距離，反推該買幾張／幾股，控制單筆風險。",
          "soon": true
        },
        {
          "title": "停損停利比試算",
          "icon": "🛡️",
          "desc": "輸入進場價、停損價、目標價，算出風險報酬比（R值），輔助判斷值不值得進場。",
          "soon": true
        },
        {
          "title": "再平衡試算",
          "icon": "🔄",
          "desc": "輸入目前各資產（股/債/現金）金額與目標配置比例，算出該加碼或減碼多少才能回到目標比例。",
          "soon": true
        }
      ]
    },
    {
      "title": "估值與基本面分析",
      "href": "valuation_analysis.html",
      "icon": "🔍",
      "keywords": "本益比 ddm dcf roe 杜邦",
      "soon": true,
      "description": "評估股價合理性與獲利品質的分析工具。",
      "homeDesc": "本益比河流圖、DDM／DCF估值、ROE杜邦拆解等分析工具。",
      "homeCta": "前往工具列表 →",
      "tools": [
        {
          "title": "本益比／股價淨值比河流圖",
          "icon": "🌊",
          "desc": "輸入歷史EPS或淨值與目前股價，畫出目前站在歷史區間的哪個百分位。",
          "soon": true
        },
        {
          "title": "股利折現模型（DDM）試算",
          "icon": "💹",
          "desc": "輸入股利、成長率、折現率，估算合理股價。",
          "soon": true
        },
        {
          "title": "DCF現金流折現試算",
          "icon": "📐",
          "desc": "輸入自由現金流與成長假設，估算內在價值，適合看現金流穩定的公司。",
          "soon": true
        },
        {
          "title": "ROE杜邦分析拆解",
          "icon": "🧩",
          "desc": "把ROE拆成淨利率×資產周轉率×財務槓桿，快速看出獲利品質來源。",
          "soon": true
        }
      ]
    },
    {
      "title": "股息與現金流規劃",
      "href": "dividend_cashflow.html",
      "icon": "💰",
      "keywords": "配息 股利 退休 4% 現金流",
      "soon": true,
      "description": "規劃配息現金流與稅務、退休提領的試算工具。",
      "homeDesc": "月配息現金流月曆、股利稅務、退休提領試算等工具。",
      "homeCta": "前往工具列表 →",
      "tools": [
        {
          "title": "月配息現金流月曆",
          "icon": "📅",
          "desc": "輸入持股清單與配息月份，試算每個月預期能收到多少股息，適合存股族。",
          "soon": true
        },
        {
          "title": "可扣抵稅額／股利所得稅試算",
          "icon": "🧾",
          "desc": "台股股利併入綜所稅計算，判斷用哪種課稅方式較划算。",
          "soon": true
        },
        {
          "title": "退休提領試算（4%法則）",
          "icon": "🏖️",
          "desc": "輸入退休資產與提領率，估算能撐幾年、每月可提領多少。",
          "soon": true
        }
      ]
    }
  ]
};
