package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss
import com.bharatstocks.ui.theme.Amber

private fun riskColor(level: String): Color = when (level.lowercase()) {
    "low" -> GreenGain
    "medium", "moderate" -> Amber
    "high" -> RedLoss
    else -> Color.Gray
}

private fun riskLabel(level: String): String = when (level.lowercase()) {
    "low" -> "Low"
    "medium", "moderate" -> "Medium"
    "high" -> "High"
    else -> level.replaceFirstChar { it.uppercase() }.ifBlank { "—" }
}

@Composable
fun RiskTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingRisk) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    val risk = uiState.risk

    if (risk == null) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No risk data available", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        return
    }

    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            OverallRiskCard(risk.overallRisk)
        }

        item {
            Text("Risk Breakdown", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                RiskRow("Valuation Risk", risk.valuationRisk)
                RiskRow("Debt Risk", risk.debtRisk)
                RiskRow("Earnings Risk", risk.earningsRisk)
                RiskRow("Promoter Risk", risk.promoterRisk)
                RiskRow("Liquidity Risk", risk.liquidityRisk)
            }
        }

        if (risk.notes.isNotBlank()) {
            item {
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Analyst Notes", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(8.dp))
                        Text(risk.notes, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    }
}

@Composable
private fun OverallRiskCard(level: String) {
    val color = riskColor(level)
    Card(
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.12f)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text("Overall Risk", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(riskLabel(level), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = color)
            }
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(color.copy(alpha = 0.25f)),
                contentAlignment = Alignment.Center
            ) {
                Text(riskLabel(level).first().toString(), style = MaterialTheme.typography.headlineLarge, color = color, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun RiskRow(label: String, level: String) {
    val color = riskColor(level)
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(label, style = MaterialTheme.typography.bodyMedium)
            Surface(
                color = color.copy(alpha = 0.15f),
                shape = RoundedCornerShape(6.dp)
            ) {
                Text(
                    riskLabel(level),
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                    color = color,
                    fontWeight = FontWeight.Medium,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}
