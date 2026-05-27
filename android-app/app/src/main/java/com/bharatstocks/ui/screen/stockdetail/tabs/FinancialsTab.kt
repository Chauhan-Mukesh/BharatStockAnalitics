package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState

private data class RatioItem(val label: String, val value: String, val description: String = "")

@Composable
fun FinancialsTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingFinancials) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    val fin = uiState.financials

    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text("Valuation Ratios", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            RatiosGrid(
                listOf(
                    RatioItem("P/E Ratio", fin?.peRatio?.let { "%.2f".format(it) } ?: "—", "Price to Earnings"),
                    RatioItem("P/B Ratio", fin?.pbRatio?.let { "%.2f".format(it) } ?: "—", "Price to Book"),
                    RatioItem("EPS", fin?.eps?.let { "₹%.2f".format(it) } ?: "—", "Earnings Per Share"),
                    RatioItem("Book Value", fin?.bookValue?.let { "₹%.2f".format(it) } ?: "—")
                )
            )
        }

        item {
            HorizontalDivider()
            Spacer(Modifier.height(4.dp))
            Text("Profitability", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            RatiosGrid(
                listOf(
                    RatioItem("ROE", fin?.roe?.let { "%.2f%%".format(it) } ?: "—", "Return on Equity"),
                    RatioItem("ROCE", fin?.roce?.let { "%.2f%%".format(it) } ?: "—", "Return on Capital Employed"),
                    RatioItem("Net Margin", fin?.netMargin?.let { "%.2f%%".format(it) } ?: "—"),
                    RatioItem("Op. Margin", fin?.operatingMargin?.let { "%.2f%%".format(it) } ?: "—")
                )
            )
        }

        item {
            HorizontalDivider()
            Spacer(Modifier.height(4.dp))
            Text("Growth (3Y CAGR)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            RatiosGrid(
                listOf(
                    RatioItem("Revenue", fin?.revenueCagr3y?.let { "%.2f%%".format(it) } ?: "—"),
                    RatioItem("Profit", fin?.profitCagr3y?.let { "%.2f%%".format(it) } ?: "—"),
                    RatioItem("EPS", fin?.epsCagr3y?.let { "%.2f%%".format(it) } ?: "—")
                )
            )
        }

        item {
            HorizontalDivider()
            Spacer(Modifier.height(4.dp))
            Text("Leverage & Dividend", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            RatiosGrid(
                listOf(
                    RatioItem("D/E Ratio", fin?.debtEquity?.let { "%.2f".format(it) } ?: "—", "Debt to Equity"),
                    RatioItem("Div. Yield", fin?.dividendYield?.let { "%.2f%%".format(it) } ?: "—")
                )
            )
        }

        if (fin == null) {
            item {
                Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                    Text("No financial data available", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun RatiosGrid(items: List<RatioItem>) {
    val chunked = items.chunked(2)
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        chunked.forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                row.forEach { item ->
                    RatioCard(item, Modifier.weight(1f))
                }
                if (row.size == 1) {
                    Spacer(Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun RatioCard(item: RatioItem, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(item.label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(4.dp))
            Text(item.value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            if (item.description.isNotBlank()) {
                Text(item.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
