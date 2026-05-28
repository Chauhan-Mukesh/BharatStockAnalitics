package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss

@Composable
fun OverviewTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingQuote || uiState.isLoadingOverview) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Quote hero card
        uiState.quote?.let { quote ->
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(quote.name, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            QuoteStatItem("Open", "₹%.2f".format(quote.open))
                            QuoteStatItem("High", "₹%.2f".format(quote.high))
                            QuoteStatItem("Low", "₹%.2f".format(quote.low))
                            QuoteStatItem("Prev Close", "₹%.2f".format(quote.prevClose))
                        }
                        Spacer(Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            QuoteStatItem("52W High", "₹%.2f".format(quote.week52High))
                            QuoteStatItem("52W Low", "₹%.2f".format(quote.week52Low))
                            QuoteStatItem("Volume", formatLargeNumber(quote.volume.toDouble()))
                            QuoteStatItem("Mkt Cap", formatLargeNumber(quote.marketCap))
                        }
                    }
                }
            }
        }

        // Chart placeholder
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Price Chart", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(Modifier.height(8.dp))
                        Text("Chart placeholder — integrate MPAndroidChart or Vico", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }

        // Company overview
        uiState.overview?.let { overview ->
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("About", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(8.dp))
                        if (overview.description.isNotBlank()) {
                            Text(overview.description, style = MaterialTheme.typography.bodyMedium)
                            Spacer(Modifier.height(12.dp))
                        }
                        OverviewRow("Sector", overview.sector)
                        OverviewRow("Industry", overview.industry)
                        OverviewRow("CEO", overview.ceo)
                        OverviewRow("Employees", if (overview.employees > 0) overview.employees.toString() else "—")
                        OverviewRow("Founded", overview.founded)
                        OverviewRow("HQ", overview.headquarters)
                        OverviewRow("Listed On", overview.listing)
                        if (overview.website.isNotBlank()) {
                            OverviewRow("Website", overview.website)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun QuoteStatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun OverviewRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value.ifBlank { "—" }, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
    }
}

internal fun formatLargeNumber(value: Double): String = when {
    value >= 1_00_00_00_000.0 -> "₹%.2fCr".format(value / 1_00_00_000.0)
    value >= 1_00_00_000.0 -> "₹%.2fCr".format(value / 1_00_00_000.0)
    value >= 1_00_000.0 -> "₹%.2fL".format(value / 1_00_000.0)
    else -> "%.0f".format(value)
}
