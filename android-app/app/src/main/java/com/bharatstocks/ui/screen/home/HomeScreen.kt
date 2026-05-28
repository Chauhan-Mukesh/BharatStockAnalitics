package com.bharatstocks.ui.screen.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss

private data class MockMover(
    val symbol: String,
    val name: String,
    val price: String,
    val change: String,
    val isGain: Boolean
)

private val mockGainers = listOf(
    MockMover("RELIANCE", "Reliance Industries", "₹2,845", "+2.4%", true),
    MockMover("HDFCBANK", "HDFC Bank", "₹1,680", "+1.8%", true),
    MockMover("INFY", "Infosys", "₹1,540", "+3.1%", true),
    MockMover("TCS", "TCS", "₹3,920", "+1.2%", true)
)

private val mockLosers = listOf(
    MockMover("WIPRO", "Wipro", "₹460", "-1.5%", false),
    MockMover("TATAMOTORS", "Tata Motors", "₹890", "-2.3%", false),
    MockMover("BAJFINANCE", "Bajaj Finance", "₹7,100", "-0.9%", false)
)

private val mockNews = listOf(
    "RBI keeps repo rate unchanged at 6.5% in latest MPC meeting",
    "Sensex hits all-time high; Nifty crosses 22,500 mark",
    "FII inflows surge ₹8,000 Cr in a single session",
    "SEBI introduces new F&O regulations for retail investors"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onStockClick: (exchange: String, symbol: String) -> Unit,
    onSearchClick: () -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        contentPadding = PaddingValues(bottom = 16.dp)
    ) {
        item {
            TopAppBar(
                title = { Text("BharatStocks", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        }

        // Search bar
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .clickable { onSearchClick() },
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 14.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Search, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    Spacer(Modifier.width(12.dp))
                    Text("Search NSE / BSE stocks…", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        // Market movers - Gainers
        item {
            SectionHeader("Top Gainers")
        }
        item {
            LazyRow(
                contentPadding = PaddingValues(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(mockGainers) { mover ->
                    MoverCard(mover, onStockClick)
                }
            }
        }

        // Market movers - Losers
        item {
            SectionHeader("Top Losers")
        }
        item {
            LazyRow(
                contentPadding = PaddingValues(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(mockLosers) { mover ->
                    MoverCard(mover, onStockClick)
                }
            }
        }

        // Watchlist snapshot
        item {
            SectionHeader("Watchlist")
        }
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Add stocks to your watchlist", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        // News
        item {
            SectionHeader("Market News")
        }
        items(mockNews) { headline ->
            NewsCard(headline)
        }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleLarge,
        modifier = Modifier.padding(start = 16.dp, top = 16.dp, bottom = 8.dp)
    )
}

@Composable
private fun MoverCard(mover: MockMover, onStockClick: (String, String) -> Unit) {
    Card(
        modifier = Modifier
            .width(150.dp)
            .clickable { onStockClick("NSE", mover.symbol) },
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(mover.symbol, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(mover.name, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1)
            Spacer(Modifier.height(8.dp))
            Text(mover.price, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.SemiBold)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (mover.isGain) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                    contentDescription = null,
                    tint = if (mover.isGain) GreenGain else RedLoss,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(Modifier.width(4.dp))
                Text(
                    text = mover.change,
                    color = if (mover.isGain) GreenGain else RedLoss,
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
private fun NewsCard(headline: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(4.dp, 40.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(MaterialTheme.colorScheme.primary)
            )
            Spacer(Modifier.width(12.dp))
            Text(headline, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
