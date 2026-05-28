package com.bharatstocks.ui.screen.portfolio

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bharatstocks.data.model.AddHoldingRequest
import com.bharatstocks.data.model.PortfolioResponse
import com.bharatstocks.data.repository.Result
import com.bharatstocks.data.repository.StockRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PortfolioUiState(
    val portfolio: PortfolioResponse? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class PortfolioViewModel @Inject constructor(
    private val repository: StockRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PortfolioUiState())
    val uiState: StateFlow<PortfolioUiState> = _uiState.asStateFlow()

    init {
        loadPortfolio()
    }

    fun loadPortfolio() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = repository.getPortfolio()) {
                is Result.Success -> _uiState.update { it.copy(portfolio = result.data, isLoading = false) }
                is Result.Error -> _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
                Result.Loading -> Unit
            }
        }
    }

    fun addHolding(symbol: String, exchange: String, quantity: Double, avgPrice: Double) {
        viewModelScope.launch {
            when (repository.addHolding(symbol, exchange, quantity, avgPrice)) {
                is Result.Success -> loadPortfolio()
                is Result.Error -> _uiState.update { it.copy(errorMessage = "Failed to add holding") }
                Result.Loading -> Unit
            }
        }
    }
}
