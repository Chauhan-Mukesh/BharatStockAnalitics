package com.bharatstocks

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.bharatstocks.ui.navigation.BharatStocksNavHost
import com.bharatstocks.ui.theme.BharatStocksTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            BharatStocksTheme {
                BharatStocksNavHost()
            }
        }
    }
}
