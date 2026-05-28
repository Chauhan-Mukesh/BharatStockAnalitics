package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.data.model.NewsItem
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss
import com.bharatstocks.ui.theme.Amber

@Composable
fun NewsTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingNews) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    if (uiState.news.isEmpty()) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No news available", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        return
    }

    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        items(uiState.news) { news ->
            NewsCard(news)
        }
    }
}

@Composable
private fun NewsCard(news: NewsItem) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    news.source,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                SentimentBadge(news.sentiment)
            }
            Spacer(Modifier.height(6.dp))
            Text(news.headline, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
            if (news.summary.isNotBlank()) {
                Spacer(Modifier.height(4.dp))
                Text(news.summary, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 3)
            }
            Spacer(Modifier.height(6.dp))
            Text(news.publishedAt, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun SentimentBadge(sentiment: String) {
    val (label, color) = when (sentiment.lowercase()) {
        "positive" -> "Positive" to GreenGain
        "negative" -> "Negative" to RedLoss
        else -> "Neutral" to Amber
    }
    Surface(
        color = color.copy(alpha = 0.15f),
        shape = RoundedCornerShape(4.dp)
    ) {
        Text(
            label,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
            color = color,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Medium
        )
    }
}
