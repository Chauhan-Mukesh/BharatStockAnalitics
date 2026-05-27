package com.bharatstocks.ui.screen.stockdetail.tabs

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.bharatstocks.data.model.PeerItem
import com.bharatstocks.ui.screen.stockdetail.StockDetailUiState
import com.bharatstocks.ui.theme.GreenGain
import com.bharatstocks.ui.theme.RedLoss

@Composable
fun PeersTab(uiState: StockDetailUiState) {
    if (uiState.isLoadingPeers) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    if (uiState.peers.isEmpty()) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No peer data available", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        return
    }

    LazyColumn(contentPadding = PaddingValues(16.dp)) {
        item {
            Text("Peer Comparison", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))
        }
        item {
            Box(modifier = Modifier.horizontalScroll(rememberScrollState())) {
                Column {
                    PeersTableHeader()
                    HorizontalDivider()
                    uiState.peers.forEach { peer ->
                        PeersTableRow(peer)
                        HorizontalDivider(thickness = 0.5.dp)
                    }
                }
            }
        }
    }
}

@Composable
private fun PeersTableHeader() {
    Row(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(vertical = 10.dp)
    ) {
        HeaderCell("Symbol", 110.dp)
        HeaderCell("Price", 90.dp)
        HeaderCell("Mkt Cap", 110.dp)
        HeaderCell("P/E", 70.dp)
        HeaderCell("P/B", 70.dp)
        HeaderCell("ROE", 70.dp)
        HeaderCell("Chg%", 80.dp)
    }
}

@Composable
private fun PeersTableRow(peer: PeerItem) {
    val isGain = peer.changePercent >= 0
    Row(
        modifier = Modifier.padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        DataCell(peer.symbol, 110.dp, bold = true)
        DataCell("₹%.2f".format(peer.price), 90.dp)
        DataCell(formatLargeNumber(peer.marketCap), 110.dp)
        DataCell("%.2f".format(peer.peRatio), 70.dp)
        DataCell("%.2f".format(peer.pbRatio), 70.dp)
        DataCell("%.2f%%".format(peer.roe), 70.dp)
        DataCell(
            "%.2f%%".format(peer.changePercent),
            80.dp,
            color = if (isGain) GreenGain else RedLoss
        )
    }
}

@Composable
private fun HeaderCell(text: String, width: androidx.compose.ui.unit.Dp) {
    Text(
        text = text,
        modifier = Modifier.width(width).padding(horizontal = 4.dp),
        style = MaterialTheme.typography.labelSmall,
        fontWeight = FontWeight.SemiBold,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        textAlign = TextAlign.End
    )
}

@Composable
private fun DataCell(
    text: String,
    width: androidx.compose.ui.unit.Dp,
    bold: Boolean = false,
    color: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.onSurface
) {
    Text(
        text = text,
        modifier = Modifier.width(width).padding(horizontal = 4.dp),
        style = MaterialTheme.typography.bodySmall,
        fontWeight = if (bold) FontWeight.SemiBold else FontWeight.Normal,
        color = color,
        textAlign = if (bold) TextAlign.Start else TextAlign.End
    )
}
