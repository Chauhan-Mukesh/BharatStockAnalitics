package com.bharatstocks.data.repository

import com.bharatstocks.data.model.*
import com.bharatstocks.data.remote.ApiService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Inject
import javax.inject.Singleton

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

@Singleton
class StockRepository @Inject constructor(
    private val api: ApiService
) {
    private val quoteCache: MutableMap<String, QuoteResponse> = ConcurrentHashMap()
    private val overviewCache: MutableMap<String, OverviewResponse> = ConcurrentHashMap()
    private val financialsCache: MutableMap<String, FinancialsResponse> = ConcurrentHashMap()
    private val technicalsCache: MutableMap<String, TechnicalsResponse> = ConcurrentHashMap()
    private val shareholdingCache: MutableMap<String, ShareholdingResponse> = ConcurrentHashMap()
    private val riskCache: MutableMap<String, RiskResponse> = ConcurrentHashMap()
    private val aiSummaryCache: MutableMap<String, AiSummaryResponse> = ConcurrentHashMap()

    private fun cacheKey(exchange: String, symbol: String) = "$exchange:$symbol"

    suspend fun searchStocks(query: String): Result<List<StockSearchResult>> =
        safeApiCall { api.searchStocks(query) }

    suspend fun getQuote(exchange: String, symbol: String): Result<QuoteResponse> {
        val key = cacheKey(exchange, symbol)
        return safeApiCall {
            api.getQuote(exchange, symbol).also { quoteCache[key] = it }
        }
    }

    suspend fun getOverview(exchange: String, symbol: String): Result<OverviewResponse> {
        val key = cacheKey(exchange, symbol)
        overviewCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getOverview(exchange, symbol).also { overviewCache[key] = it }
        }
    }

    suspend fun getFinancials(exchange: String, symbol: String): Result<FinancialsResponse> {
        val key = cacheKey(exchange, symbol)
        financialsCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getFinancials(exchange, symbol).also { financialsCache[key] = it }
        }
    }

    suspend fun getTechnicals(exchange: String, symbol: String): Result<TechnicalsResponse> {
        val key = cacheKey(exchange, symbol)
        technicalsCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getTechnicals(exchange, symbol).also { technicalsCache[key] = it }
        }
    }

    suspend fun getShareholding(exchange: String, symbol: String): Result<ShareholdingResponse> {
        val key = cacheKey(exchange, symbol)
        shareholdingCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getShareholding(exchange, symbol).also { shareholdingCache[key] = it }
        }
    }

    suspend fun getFilings(exchange: String, symbol: String): Result<List<FilingItem>> =
        safeApiCall { api.getFilings(exchange, symbol) }

    suspend fun getNews(exchange: String, symbol: String): Result<List<NewsItem>> =
        safeApiCall { api.getNews(exchange, symbol) }

    suspend fun getRisk(exchange: String, symbol: String): Result<RiskResponse> {
        val key = cacheKey(exchange, symbol)
        riskCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getRisk(exchange, symbol).also { riskCache[key] = it }
        }
    }

    suspend fun getPeers(exchange: String, symbol: String): Result<List<PeerItem>> =
        safeApiCall { api.getPeers(exchange, symbol) }

    suspend fun getAiSummary(exchange: String, symbol: String): Result<AiSummaryResponse> {
        val key = cacheKey(exchange, symbol)
        aiSummaryCache[key]?.let { return Result.Success(it) }
        return safeApiCall {
            api.getAiSummary(exchange, symbol).also { aiSummaryCache[key] = it }
        }
    }

    suspend fun getWatchlists(): Result<List<Watchlist>> =
        safeApiCall { api.getWatchlists() }

    suspend fun createWatchlist(name: String): Result<Watchlist> =
        safeApiCall { api.createWatchlist(CreateWatchlistRequest(name)) }

    suspend fun addToWatchlist(id: Int, symbol: String, exchange: String): Result<Unit> =
        safeApiCall { api.addToWatchlist(id, AddStockRequest(symbol, exchange)) }

    suspend fun getPortfolio(): Result<PortfolioResponse> =
        safeApiCall { api.getPortfolio() }

    suspend fun addHolding(symbol: String, exchange: String, quantity: Double, avgPrice: Double): Result<Unit> =
        safeApiCall { api.addHolding(AddHoldingRequest(symbol, exchange, quantity, avgPrice)) }

    fun clearCache() {
        quoteCache.clear()
        overviewCache.clear()
        financialsCache.clear()
        technicalsCache.clear()
        shareholdingCache.clear()
        riskCache.clear()
        aiSummaryCache.clear()
    }

    private suspend fun <T> safeApiCall(call: suspend () -> T): Result<T> =
        withContext(Dispatchers.IO) {
            try {
                Result.Success(call())
            } catch (e: Exception) {
                Result.Error(e.message ?: "Unknown error", e)
            }
        }
}
