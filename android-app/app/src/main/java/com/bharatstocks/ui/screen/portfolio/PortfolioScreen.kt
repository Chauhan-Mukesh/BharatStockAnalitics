package com.bharatstocks.ui.screen.portfolio

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.bharatstocks.data.model.PortfolioHolding
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PortfolioScreen(
    viewModel: PortfolioViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Portfolio", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            return@Scaffold
        }

        val portfolio = uiState.portfolio

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            if (portfolio == null) {
                item {
                    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("No portfolio data", color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(Modifier.height(8.dp))
                            Button(onClick = { viewModel.loadPortfolio() }) {
                                Text("Retry")
                            }
                        }
                    }
                }
                return@LazyColumn
            }

            // Summary card
            item {
                val isGain = portfolio.totalGain >= 0
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isGain) GreenGain.copy(alpha = 0.1f) else RedLoss.copy(alpha = 0.1f)
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Total Value", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(
                            "₹%.2f".format(portfolio.currentValue),
                            style = MaterialTheme.typography.displayMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(Modifier.height(12.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            SummaryItem("Invested", "₹%.2f".format(portfolio.totalInvested), Modifier.weight(1f))
                            SummaryItem(
                                "P&L",
                                "%s₹%.2f (%.2f%%)".format(if (isGain) "+" else "", portfolio.totalGain, portfolio.gainPercent),
                                Modifier.weight(1f),
                                color = if (isGain) GreenGain else RedLoss
                            )
                            SummaryItem(
                                "Day Gain",
                                "%s₹%.2f".format(if (portfolio.dayGain >= 0) "+" else "", portfolio.dayGain),
                                Modifier.weight(1f),
                                color = if (portfolio.dayGain >= 0) GreenGain else RedLoss
                            )
                        }
                    }
                }
            }

            item {
                Text("Holdings (${portfolio.holdings.size})", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            }

            items(portfolio.holdings) { holding ->
                HoldingCard(holding)
            }
        }
    }
}

@Composable
private fun SummaryItem(label: String, value: String, modifier: Modifier = Modifier, color: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.onSurface) {
    Column(modifier = modifier) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium, color = color)
    }
}

@Composable
private fun HoldingCard(holding: PortfolioHolding) {
    val isGain = holding.gain >= 0
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(holding.symbol, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text("${holding.exchange}  •  Qty: ${holding.quantity.toLong()}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text("₹%.2f".format(holding.currentPrice), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Text(
                        "Avg ₹%.2f".format(holding.avgPrice),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            Spacer(Modifier.height(8.dp))
            HorizontalDivider(thickness = 0.5.dp)
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                HoldingStatItem("Invested", "₹%.2f".format(holding.invested))
                HoldingStatItem("Current", "₹%.2f".format(holding.currentValue))
                HoldingStatItem(
                    "P&L",
                    "%s₹%.2f\n(%.2f%%)".format(if (isGain) "+" else "", holding.gain, holding.gainPercent),
                    color = if (isGain) GreenGain else RedLoss
                )
            }
        }
    }
}

@Composable
private fun HoldingStatItem(label: String, value: String, color: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.onSurface) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium, color = color, textAlign = TextAlign.Center)
    }
}
