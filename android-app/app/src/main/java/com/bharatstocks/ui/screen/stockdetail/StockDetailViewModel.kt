package com.bharatstocks.ui.screen.stockdetail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bharatstocks.data.model.*
import com.bharatstocks.data.repository.Result
import com.bharatstocks.data.repository.StockRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class StockDetailUiState(
    val exchange: String = "",
    val symbol: String = "",
    val quote: QuoteResponse? = null,
    val overview: OverviewResponse? = null,
    val financials: FinancialsResponse? = null,
    val technicals: TechnicalsResponse? = null,
    val shareholding: ShareholdingResponse? = null,
    val news: List<NewsItem> = emptyList(),
    val risk: RiskResponse? = null,
    val peers: List<PeerItem> = emptyList(),
    val aiSummary: AiSummaryResponse? = null,
    val isLoadingQuote: Boolean = false,
    val isLoadingOverview: Boolean = false,
    val isLoadingFinancials: Boolean = false,
    val isLoadingTechnicals: Boolean = false,
    val isLoadingShareholding: Boolean = false,
    val isLoadingNews: Boolean = false,
    val isLoadingRisk: Boolean = false,
    val isLoadingPeers: Boolean = false,
    val isLoadingAi: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class StockDetailViewModel @Inject constructor(
    private val repository: StockRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(StockDetailUiState())
    val uiState: StateFlow<StockDetailUiState> = _uiState.asStateFlow()

    fun load(exchange: String, symbol: String) {
        _uiState.update { it.copy(exchange = exchange, symbol = symbol) }
        loadQuote(exchange, symbol)
        loadOverview(exchange, symbol)
    }

    fun loadQuote(exchange: String, symbol: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingQuote = true) }
            when (val r = repository.getQuote(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(quote = r.data, isLoadingQuote = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingQuote = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadOverview(exchange: String, symbol: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingOverview = true) }
            when (val r = repository.getOverview(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(overview = r.data, isLoadingOverview = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingOverview = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadFinancials(exchange: String, symbol: String) {
        if (_uiState.value.financials != null) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingFinancials = true) }
            when (val r = repository.getFinancials(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(financials = r.data, isLoadingFinancials = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingFinancials = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadTechnicals(exchange: String, symbol: String) {
        if (_uiState.value.technicals != null) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingTechnicals = true) }
            when (val r = repository.getTechnicals(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(technicals = r.data, isLoadingTechnicals = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingTechnicals = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadShareholding(exchange: String, symbol: String) {
        if (_uiState.value.shareholding != null) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingShareholding = true) }
            when (val r = repository.getShareholding(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(shareholding = r.data, isLoadingShareholding = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingShareholding = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadNews(exchange: String, symbol: String) {
        if (_uiState.value.news.isNotEmpty()) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingNews = true) }
            when (val r = repository.getNews(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(news = r.data, isLoadingNews = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingNews = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadRisk(exchange: String, symbol: String) {
        if (_uiState.value.risk != null) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingRisk = true) }
            when (val r = repository.getRisk(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(risk = r.data, isLoadingRisk = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingRisk = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadPeers(exchange: String, symbol: String) {
        if (_uiState.value.peers.isNotEmpty()) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingPeers = true) }
            when (val r = repository.getPeers(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(peers = r.data, isLoadingPeers = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingPeers = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun loadAiSummary(exchange: String, symbol: String) {
        if (_uiState.value.aiSummary != null) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingAi = true) }
            when (val r = repository.getAiSummary(exchange, symbol)) {
                is Result.Success -> _uiState.update { it.copy(aiSummary = r.data, isLoadingAi = false) }
                is Result.Error -> _uiState.update { it.copy(isLoadingAi = false, errorMessage = r.message) }
                Result.Loading -> Unit
            }
        }
    }
}
