package com.bharatstocks.ui.screen.stockdetail

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.bharatstocks.ui.screen.stockdetail.tabs.*
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss

private val tabs = listOf(
    "Overview", "Financials", "Technicals", "Shareholding",
    "News", "Risk", "Peers", "AI Summary"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StockDetailScreen(
    exchange: String,
    symbol: String,
    onBack: () -> Unit,
    viewModel: StockDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedTabIndex by remember { mutableIntStateOf(0) }

    LaunchedEffect(exchange, symbol) {
        viewModel.load(exchange, symbol)
    }

    LaunchedEffect(selectedTabIndex) {
        when (selectedTabIndex) {
            1 -> viewModel.loadFinancials(exchange, symbol)
            2 -> viewModel.loadTechnicals(exchange, symbol)
            3 -> viewModel.loadShareholding(exchange, symbol)
            4 -> viewModel.loadNews(exchange, symbol)
            5 -> viewModel.loadRisk(exchange, symbol)
            6 -> viewModel.loadPeers(exchange, symbol)
            7 -> viewModel.loadAiSummary(exchange, symbol)
        }
    }

    Scaffold(
        topBar = {
            Column {
                TopAppBar(
                    title = {
                        Column {
                            Text(symbol, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                            Text(exchange, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                        }
                    },
                    actions = {
                        uiState.quote?.let { quote ->
                            val isGain = quote.change >= 0
                            Column(
                                horizontalAlignment = Alignment.End,
                                modifier = Modifier.padding(end = 16.dp)
                            ) {
                                Text(
                                    "₹%.2f".format(quote.price),
                                    style = MaterialTheme.typography.titleLarge,
                                    fontWeight = FontWeight.Bold
                                )
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = if (isGain) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                                        contentDescription = null,
                                        tint = if (isGain) GreenGain else RedLoss,
                                        modifier = Modifier.size(14.dp)
                                    )
                                    Spacer(Modifier.width(4.dp))
                                    Text(
                                        "%.2f (%.2f%%)".format(quote.change, quote.changePercent),
                                        color = if (isGain) GreenGain else RedLoss,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                            }
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
                )
                ScrollableTabRow(
                    selectedTabIndex = selectedTabIndex,
                    edgePadding = 0.dp,
                    containerColor = MaterialTheme.colorScheme.background
                ) {
                    tabs.forEachIndexed { index, title ->
                        Tab(
                            selected = selectedTabIndex == index,
                            onClick = { selectedTabIndex = index },
                            text = { Text(title, style = MaterialTheme.typography.labelLarge) }
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (selectedTabIndex) {
                0 -> OverviewTab(uiState)
                1 -> FinancialsTab(uiState)
                2 -> TechnicalsTab(uiState)
                3 -> ShareholdingTab(uiState)
                4 -> NewsTab(uiState)
                5 -> RiskTab(uiState)
                6 -> PeersTab(uiState)
                7 -> AiSummaryTab(uiState)
            }
        }
    }
}
