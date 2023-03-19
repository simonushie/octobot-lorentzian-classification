import enum


class LivePlottingModes(enum.Enum):
    DISABLE_PLOTTING = "disable live plotting"
    PLOT_RECORDING_MODE = "plot recording mode"
    REPLOT_VISIBLE_HISTORY = "replot visible history"


class BacktestPlottingModes(enum.Enum):
    DISABLE_PLOTTING = "disable backtest indicator plotting"
    ENABLE_PLOTTING = "enable backtest indicator plotting"


CURRENT_TIME_FRAME = "current time frame"


class TradingModeCommands:
    EXECUTE = "execute"
    ACTIVATE_REALTIME_STRATEGY = "activate_realtime_strategy"
    DISABLE_REALTIME_STRATEGY = "disable_realtime_strategy"
    SAVE = "save"
    INIT_CALL = "init_call"
    OHLC_CALLBACK = "ohlc_callback"
    KLINE_CALLBACK = "kline_callback"


# TODO remove when merged into octobot
class UserInputEditorOptionsTypes(enum.Enum):
    GRID_COLUMNS = "grid_columns"
    COLLAPSED = "collapsed"
    
    
class UserInputOtherSchemaValuesTypes(enum.Enum):
    DISPLAY_AS_TAB = "display_as_tab"  # used by octo ui2
    DESCRIPTION = "description"