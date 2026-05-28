package com.bharatstocks.ui.screen.watchlist

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bharatstocks.data.model.Watchlist
import com.bharatstocks.data.repository.Result
import com.bharatstocks.data.repository.StockRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class WatchlistUiState(
    val watchlists: List<Watchlist> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class WatchlistViewModel @Inject constructor(
    private val repository: StockRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(WatchlistUiState())
    val uiState: StateFlow<WatchlistUiState> = _uiState.asStateFlow()

    init {
        loadWatchlists()
    }

    fun loadWatchlists() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = repository.getWatchlists()) {
                is Result.Success -> _uiState.update { it.copy(watchlists = result.data, isLoading = false) }
                is Result.Error -> _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun createWatchlist(name: String) {
        if (name.isBlank()) return
        viewModelScope.launch {
            when (repository.createWatchlist(name)) {
                is Result.Success -> loadWatchlists()
                is Result.Error -> _uiState.update { it.copy(errorMessage = "Failed to create watchlist") }
                Result.Loading -> Unit
            }
        }
    }

    fun addStock(watchlistId: Int, symbol: String, exchange: String) {
        viewModelScope.launch {
            when (repository.addToWatchlist(watchlistId, symbol, exchange)) {
                is Result.Success -> loadWatchlists()
                is Result.Error -> _uiState.update { it.copy(errorMessage = "Failed to add stock") }
                Result.Loading -> Unit
            }
        }
    }
}
