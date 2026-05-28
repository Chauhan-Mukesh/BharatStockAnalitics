package com.bharatstocks.data.model

import com.google.gson.annotations.SerializedName

data class StockSearchResult(
    val symbol: String = "",
    val name: String = "",
    val exchange: String = "",
    val type: String = ""
)

data class QuoteResponse(
    val symbol: String = "",
    val name: String = "",
    val exchange: String = "",
    val price: Double = 0.0,
    val change: Double = 0.0,
    @SerializedName("change_percent") val changePercent: Double = 0.0,
    val open: Double = 0.0,
    val high: Double = 0.0,
    val low: Double = 0.0,
    @SerializedName("prev_close") val prevClose: Double = 0.0,
    val volume: Long = 0L,
    @SerializedName("market_cap") val marketCap: Double = 0.0,
    @SerializedName("52w_high") val week52High: Double = 0.0,
    @SerializedName("52w_low") val week52Low: Double = 0.0
)

data class OverviewResponse(
    val symbol: String = "",
    val name: String = "",
    val sector: String = "",
    val industry: String = "",
    val description: String = "",
    val website: String = "",
    val ceo: String = "",
    val employees: Long = 0L,
    val founded: String = "",
    val headquarters: String = "",
    val listing: String = ""
)

data class FinancialsResponse(
    val symbol: String = "",
    @SerializedName("pe_ratio") val peRatio: Double = 0.0,
    @SerializedName("pb_ratio") val pbRatio: Double = 0.0,
    val roe: Double = 0.0,
    val roce: Double = 0.0,
    @SerializedName("debt_equity") val debtEquity: Double = 0.0,
    @SerializedName("net_margin") val netMargin: Double = 0.0,
    @SerializedName("operating_margin") val operatingMargin: Double = 0.0,
    @SerializedName("revenue_cagr_3y") val revenueCagr3y: Double = 0.0,
    @SerializedName("profit_cagr_3y") val profitCagr3y: Double = 0.0,
    @SerializedName("eps_cagr_3y") val epsCagr3y: Double = 0.0,
    @SerializedName("book_value") val bookValue: Double = 0.0,
    val eps: Double = 0.0,
    @SerializedName("dividend_yield") val dividendYield: Double = 0.0
)

data class TechnicalsResponse(
    val symbol: String = "",
    val rsi: Double = 0.0,
    @SerializedName("macd_line") val macdLine: Double = 0.0,
    @SerializedName("macd_signal") val macdSignal: Double = 0.0,
    @SerializedName("macd_histogram") val macdHistogram: Double = 0.0,
    @SerializedName("sma_20") val sma20: Double = 0.0,
    @SerializedName("sma_50") val sma50: Double = 0.0,
    @SerializedName("sma_200") val sma200: Double = 0.0,
    @SerializedName("ema_20") val ema20: Double = 0.0,
    @SerializedName("ema_50") val ema50: Double = 0.0,
    @SerializedName("atr") val atr: Double = 0.0,
    @SerializedName("bollinger_upper") val bollingerUpper: Double = 0.0,
    @SerializedName("bollinger_lower") val bollingerLower: Double = 0.0,
    val trend: String = ""
)

data class ShareholdingResponse(
    val symbol: String = "",
    val promoters: Double = 0.0,
    @SerializedName("fii_dii") val fiiDii: Double = 0.0,
    val fii: Double = 0.0,
    val dii: Double = 0.0,
    val public: Double = 0.0,
    val others: Double = 0.0,
    @SerializedName("pledged_percent") val pledgedPercent: Double = 0.0,
    @SerializedName("as_of") val asOf: String = ""
)

data class FilingItem(
    val id: String = "",
    val title: String = "",
    val type: String = "",
    val date: String = "",
    val url: String = ""
)

data class NewsItem(
    val id: String = "",
    val headline: String = "",
    val source: String = "",
    val publishedAt: String = "",
    val url: String = "",
    val sentiment: String = "neutral",
    val summary: String = ""
)

data class RiskResponse(
    val symbol: String = "",
    @SerializedName("overall_risk") val overallRisk: String = "",
    @SerializedName("valuation_risk") val valuationRisk: String = "",
    @SerializedName("debt_risk") val debtRisk: String = "",
    @SerializedName("earnings_risk") val earningsRisk: String = "",
    @SerializedName("promoter_risk") val promoterRisk: String = "",
    @SerializedName("liquidity_risk") val liquidityRisk: String = "",
    val notes: String = ""
)

data class PeerItem(
    val symbol: String = "",
    val name: String = "",
    val price: Double = 0.0,
    @SerializedName("market_cap") val marketCap: Double = 0.0,
    @SerializedName("pe_ratio") val peRatio: Double = 0.0,
    @SerializedName("pb_ratio") val pbRatio: Double = 0.0,
    val roe: Double = 0.0,
    @SerializedName("change_percent") val changePercent: Double = 0.0
)

data class AiSummaryResponse(
    val symbol: String = "",
    val summary: String = "",
    val sentiment: String = "",
    val keyPoints: List<String> = emptyList(),
    val disclaimer: String = ""
)

data class Watchlist(
    val id: Int = 0,
    val name: String = "",
    val stocks: List<WatchlistStock> = emptyList(),
    @SerializedName("created_at") val createdAt: String = ""
)

data class WatchlistStock(
    val symbol: String = "",
    val exchange: String = "",
    val name: String = ""
)

data class CreateWatchlistRequest(
    val name: String
)

data class AddStockRequest(
    val symbol: String,
    val exchange: String
)

data class PortfolioResponse(
    @SerializedName("total_invested") val totalInvested: Double = 0.0,
    @SerializedName("current_value") val currentValue: Double = 0.0,
    @SerializedName("total_gain") val totalGain: Double = 0.0,
    @SerializedName("gain_percent") val gainPercent: Double = 0.0,
    @SerializedName("day_gain") val dayGain: Double = 0.0,
    val holdings: List<PortfolioHolding> = emptyList()
)

data class PortfolioHolding(
    val symbol: String = "",
    val exchange: String = "",
    val name: String = "",
    val quantity: Double = 0.0,
    @SerializedName("avg_price") val avgPrice: Double = 0.0,
    @SerializedName("current_price") val currentPrice: Double = 0.0,
    @SerializedName("invested") val invested: Double = 0.0,
    @SerializedName("current_value") val currentValue: Double = 0.0,
    @SerializedName("gain") val gain: Double = 0.0,
    @SerializedName("gain_percent") val gainPercent: Double = 0.0
)

data class AddHoldingRequest(
    val symbol: String,
    val exchange: String,
    val quantity: Double,
    @SerializedName("avg_price") val avgPrice: Double
)

data class AlertItem(
    val id: String = "",
    val symbol: String = "",
    val exchange: String = "",
    val type: String = "",
    @SerializedName("target_price") val targetPrice: Double = 0.0,
    val condition: String = "",
    val active: Boolean = true,
    @SerializedName("created_at") val createdAt: String = ""
)
