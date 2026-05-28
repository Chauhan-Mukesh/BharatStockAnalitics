package com.bharatstocks.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = GreenGain,
    onPrimary = DarkBackground,
    primaryContainer = GreenGainDim,
    onPrimaryContainer = GreenGain,
    secondary = AccentBlue,
    onSecondary = DarkBackground,
    secondaryContainer = DarkElevated,
    onSecondaryContainer = OnSurfacePrimary,
    tertiary = AccentPurple,
    error = RedLoss,
    errorContainer = RedLossDim,
    background = DarkBackground,
    onBackground = OnSurfacePrimary,
    surface = DarkSurface,
    onSurface = OnSurfacePrimary,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = OnSurfaceSecondary,
    outline = OnSurfaceDisabled
)

private val LightColorScheme = lightColorScheme(
    primary = GreenGain,
    onPrimary = LightBackground,
    secondary = AccentBlue,
    background = LightBackground,
    surface = LightSurface,
    error = RedLoss
)

@Composable
fun BharatStocksTheme(
    darkTheme: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = BharatStocksTypography,
        content = content
    )
}
