package com.bharatstocks.data.remote

import com.bharatstocks.data.model.*
import retrofit2.http.*

interface ApiService {

    @GET("api/stocks/search")
    suspend fun searchStocks(@Query("q") q: String): List<StockSearchResult>

    @GET("api/stocks/{exchange}/{symbol}/quote")
    suspend fun getQuote(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): QuoteResponse

    @GET("api/stocks/{exchange}/{symbol}/overview")
    suspend fun getOverview(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): OverviewResponse

    @GET("api/stocks/{exchange}/{symbol}/financials")
    suspend fun getFinancials(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): FinancialsResponse

    @GET("api/stocks/{exchange}/{symbol}/technicals")
    suspend fun getTechnicals(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): TechnicalsResponse

    @GET("api/stocks/{exchange}/{symbol}/shareholding")
    suspend fun getShareholding(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): ShareholdingResponse

    @GET("api/stocks/{exchange}/{symbol}/filings")
    suspend fun getFilings(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): List<FilingItem>

    @GET("api/stocks/{exchange}/{symbol}/news")
    suspend fun getNews(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): List<NewsItem>

    @GET("api/stocks/{exchange}/{symbol}/risk")
    suspend fun getRisk(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): RiskResponse

    @GET("api/stocks/{exchange}/{symbol}/peers")
    suspend fun getPeers(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): List<PeerItem>

    @GET("api/stocks/{exchange}/{symbol}/ai-summary")
    suspend fun getAiSummary(
        @Path("exchange") exchange: String,
        @Path("symbol") symbol: String
    ): AiSummaryResponse

    @GET("api/watchlists")
    suspend fun getWatchlists(): List<Watchlist>

    @POST("api/watchlists")
    suspend fun createWatchlist(@Body body: CreateWatchlistRequest): Watchlist

    @POST("api/watchlists/{id}/stocks")
    suspend fun addToWatchlist(
        @Path("id") id: Int,
        @Body body: AddStockRequest
    )

    @GET("api/portfolio")
    suspend fun getPortfolio(): PortfolioResponse

    @POST("api/portfolio/holdings")
    suspend fun addHolding(@Body body: AddHoldingRequest)
}
