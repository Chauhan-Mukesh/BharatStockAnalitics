package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss
import com.bharatstocks.ui.theme.Amber

@Composable
fun TechnicalsTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingTechnicals) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    val tech = uiState.technicals

    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            // Chart placeholder
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Technical Chart Placeholder", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        item {
            Text("Trend Signal", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            val trend = tech?.trend ?: "—"
            val trendColor = when (trend.lowercase()) {
                "bullish" -> GreenGain
                "bearish" -> RedLoss
                else -> Amber
            }
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Overall Trend", style = MaterialTheme.typography.bodyLarge)
                    Text(trend.replaceFirstChar { it.uppercase() }, color = trendColor, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                }
            }
        }

        item {
            Text("Momentum Indicators", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                IndicatorCard("RSI (14)", tech?.rsi?.let { "%.2f".format(it) } ?: "—",
                    hint = when {
                        tech == null -> "—"
                        tech.rsi > 70 -> "Overbought"
                        tech.rsi < 30 -> "Oversold"
                        else -> "Neutral"
                    }
                )
                IndicatorCard("MACD Line", tech?.macdLine?.let { "%.4f".format(it) } ?: "—")
                IndicatorCard("MACD Signal", tech?.macdSignal?.let { "%.4f".format(it) } ?: "—")
                IndicatorCard("MACD Histogram", tech?.macdHistogram?.let { "%.4f".format(it) } ?: "—")
                IndicatorCard("ATR", tech?.atr?.let { "%.2f".format(it) } ?: "—")
            }
        }

        item {
            Text("Moving Averages", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                IndicatorCard("SMA 20", tech?.sma20?.let { "₹%.2f".format(it) } ?: "—")
                IndicatorCard("SMA 50", tech?.sma50?.let { "₹%.2f".format(it) } ?: "—")
                IndicatorCard("SMA 200", tech?.sma200?.let { "₹%.2f".format(it) } ?: "—")
                IndicatorCard("EMA 20", tech?.ema20?.let { "₹%.2f".format(it) } ?: "—")
                IndicatorCard("EMA 50", tech?.ema50?.let { "₹%.2f".format(it) } ?: "—")
            }
        }

        item {
            Text("Bollinger Bands", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                IndicatorCard("Upper Band", tech?.bollingerUpper?.let { "₹%.2f".format(it) } ?: "—")
                IndicatorCard("Lower Band", tech?.bollingerLower?.let { "₹%.2f".format(it) } ?: "—")
            }
        }
    }
}

@Composable
private fun IndicatorCard(label: String, value: String, hint: String = "") {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (hint.isNotBlank()) {
                    Text(hint, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}
