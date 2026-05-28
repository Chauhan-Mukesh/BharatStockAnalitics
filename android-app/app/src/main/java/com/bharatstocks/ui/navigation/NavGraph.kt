package com.bharatstocks.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.PieChart
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.bharatstocks.ui.screen.home.HomeScreen
import com.bharatstocks.ui.screen.portfolio.PortfolioScreen
import com.bharatstocks.ui.screen.search.SearchScreen
import com.bharatstocks.ui.screen.stockdetail.StockDetailScreen
import com.bharatstocks.ui.screen.watchlist.WatchlistScreen

sealed class Screen(val route: String, val label: String) {
    object Home : Screen("home", "Home")
    object Search : Screen("search", "Search")
    object Portfolio : Screen("portfolio", "Portfolio")
    object Watchlist : Screen("watchlist", "Watchlist")
    object StockDetail : Screen("stockDetail/{exchange}/{symbol}", "Detail") {
        fun createRoute(exchange: String, symbol: String) = "stockDetail/$exchange/$symbol"
    }
}

private val bottomNavItems = listOf(
    Screen.Home to Icons.Default.Home,
    Screen.Search to Icons.Default.Search,
    Screen.Portfolio to Icons.Default.PieChart,
    Screen.Watchlist to Icons.Default.Star
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BharatStocksNavHost() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val showBottomBar = currentDestination?.route?.startsWith("stockDetail") == false

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomNavItems.forEach { (screen, icon) ->
                        NavigationBarItem(
                            icon = { Icon(icon, contentDescription = screen.label) },
                            label = { Text(screen.label) },
                            selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Home.route) {
                HomeScreen(
                    onStockClick = { exchange, symbol ->
                        navController.navigate(Screen.StockDetail.createRoute(exchange, symbol))
                    },
                    onSearchClick = { navController.navigate(Screen.Search.route) }
                )
            }
            composable(Screen.Search.route) {
                SearchScreen(
                    onStockClick = { exchange, symbol ->
                        navController.navigate(Screen.StockDetail.createRoute(exchange, symbol))
                    }
                )
            }
            composable(
                route = Screen.StockDetail.route,
                arguments = listOf(
                    navArgument("exchange") { type = NavType.StringType },
                    navArgument("symbol") { type = NavType.StringType }
                )
            ) { backStackEntry ->
                val exchange = backStackEntry.arguments?.getString("exchange") ?: ""
                val symbol = backStackEntry.arguments?.getString("symbol") ?: ""
                StockDetailScreen(
                    exchange = exchange,
                    symbol = symbol,
                    onBack = { navController.popBackStack() }
                )
            }
            composable(Screen.Portfolio.route) {
                PortfolioScreen()
            }
            composable(Screen.Watchlist.route) {
                WatchlistScreen(
                    onStockClick = { exchange, symbol ->
                        navController.navigate(Screen.StockDetail.createRoute(exchange, symbol))
                    }
                )
            }
        }
    }
}
