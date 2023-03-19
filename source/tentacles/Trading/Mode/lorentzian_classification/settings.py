import octobot_commons.constants as commons_constants
import octobot_commons.enums as enums
import tentacles.Meta.Keywords.matrix_library.basic_tentacles.basic_modes.mode_base.abstract_mode_base as abstract_mode_base
import tentacles.Meta.Keywords.matrix_library.basic_tentacles.matrix_basic_keywords.matrix_enums as matrix_enums
import tentacles.Trading.Mode.lorentzian_classification.utils as utils


class LorentzianClassificationModeInputs(abstract_mode_base.AbstractBaseMode):
    general_settings: utils.GeneralSettings = None
    filter_settings: utils.FilterSettings = None
    feature_engineering_settings: utils.FeatureEngineeringSettings = None
    kernel_settings: utils.KernelSettings = None
    display_settings: utils.DisplaySettings = None
    show_trade_stats: bool = None
    use_worst_case_estimates: bool = None
    GENERAL_SETTINGS_NAME = "general_settings"
    FEATURE_ENGINEERING_SETTINGS_NAME = "feature_engineering_settings"
    FILTER_SETTINGS_NAME = "filter_settings"
    ORDER_SETTINGS_NAME = "order_settings"
    KERNEL_SETTINGS_NAME = "kernel_settings"
    DISPLAY_SETTINGS_NAME = "display_settings"

    def init_user_inputs(self, inputs: dict) -> None:
        """
        Called right before starting the trading mode,
        should define all the trading mode's user inputs
        """
        self._init_general_settings(inputs)
        self._init_order_settings(inputs)
        self._init_feature_engineering_settings(inputs)
        self._init_filter_settings(inputs)
        self._init_kernel_settings(inputs)
        self._init_display_settings(inputs)

    def _init_general_settings(self, inputs: dict) -> None:
        self.UI.user_input(
            self.GENERAL_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="General Settings",
        )
        source = self.UI.user_input(
            "candle_source",
            enums.UserInputTypes.OPTIONS,
            enums.PriceStrings.STR_PRICE_CLOSE.value,
            inputs,
            options=[
                enums.PriceStrings.STR_PRICE_CLOSE.value,
                enums.PriceStrings.STR_PRICE_OPEN.value,
                enums.PriceStrings.STR_PRICE_HIGH.value,
                enums.PriceStrings.STR_PRICE_LOW.value,
                "hlc3",
                "ohlc4",
            ],
            title="Candle source",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={"description": "Source of the input data"},
        )
        neighbors_count = self.UI.user_input(
            "neighbors_count",
            enums.UserInputTypes.INT,
            8,
            inputs,
            min_val=1,
            max_val=100,
            title="Neighbors Count",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={"description": "Number of neighbors to consider"},
        )
        use_remote_fractals = self.UI.user_input(
            "use_remote_fractals",
            enums.UserInputTypes.BOOLEAN,
            False,
            inputs,
            title="Use Remote Fractals",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={
                "description": "When the option is enabled, the model will utilize "
                "training data from the first bar up to a maximum of X bars in the "
                "past. On the other hand, if the option is disabled, the model will use"
                " training data from the current bar up to a maximum of X bars in the "
                "past. When enabled during backtesting, the starting index for each "
                'candle iteration will be determined by the "Amount of historical '
                'live candles" setting. '
                "Although this approach may yield outcomes that differ from those "
                "observed on TradingView, it can provide valuable insights. "
            },
        )
        use_down_sampling = self.UI.user_input(
            "use_down_sampling",
            enums.UserInputTypes.BOOLEAN,
            True,
            inputs,
            title="Use Down Sampling",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={
                "description": "When enabled, the strategy will only use every Xth "
                "candle as training data within the max bars back. This will speed up "
                "classification and allows you to use a higher max bars back instead, "
                "which will result in a more diverse training data."
            },
        )
        only_train_on_every_x_bars = None
        if use_down_sampling:
            only_train_on_every_x_bars = self.UI.user_input(
                "only_train_on_every_x_bars",
                enums.UserInputTypes.INT,
                4,
                inputs,
                min_val=2,
                title="Only train on every X bars",
                parent_input_name=self.GENERAL_SETTINGS_NAME,
                other_schema_values={
                    "description": "Instead of using every bar as training data, "
                    "you can instead skip candles and only train on every X bars. "
                    "This will speed up classification and allows you to increase the "
                    "max bars back."
                },
            )

        max_bars_back = self.UI.user_input(
            "max_bars_back",
            enums.UserInputTypes.INT,
            2000,
            inputs,
            min_val=1,
            title="Max Bars Back",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={
                "description": 'Make sure the "Amount of historical live candles" in '
                "the TimeframeStrategy is at least 200 bars more than this value"
            },
        )
        color_compression = 1
        # color_compression=self.UI.user_input(
        #     "color_compression",
        #     enums.UserInputTypes.INT,
        #     1,
        #     inputs,
        #     min_val=1,
        #     max_val=10,
        #     title="Color Compression",
        #     parent_input_name=self.GENERAL_SETTINGS_NAME,
        #     other_schema_values={
        #         "description": "Compression factor for adjusting the "
        #         "intensity of the color scale."
        #     },
        # )
        exit_type = self.UI.user_input(
            "exit_type",
            enums.UserInputTypes.OPTIONS,
            utils.ExitTypes.SWITCH_SIDES,
            inputs,
            options=[
                utils.ExitTypes.FOUR_BARS,
                # utils.ExitTypes.DYNAMIC,
                utils.ExitTypes.SWITCH_SIDES,
            ],
            title="Exit Type",
            parent_input_name=self.GENERAL_SETTINGS_NAME,
            other_schema_values={
                "description": "Four bars: Exits will occour exactly 4 bars "
                "after the entry. - "
                "Dynamic: attempts to let profits ride by dynamically adjusting "
                "the exit threshold based on kernel regression logic. - "
                "Switch sides: The position will switch sides on each signal.",
            },
        )
        self.general_settings = utils.GeneralSettings(
            source=source,
            neighbors_count=neighbors_count,
            use_remote_fractals=use_remote_fractals,
            use_down_sampling=use_down_sampling,
            only_train_on_every_x_bars=only_train_on_every_x_bars,
            live_history_size=self.config[
                commons_constants.CONFIG_TENTACLES_REQUIRED_CANDLES_COUNT
            ],
            max_bars_back=max_bars_back,
            color_compression=color_compression,
            exit_type=exit_type,
        )
        # Trade Stats Settings
        # Note: The trade stats section is NOT intended to be used as a replacement for
        # proper backtesting. It is intended to be used for calibration purposes only.
        # self.show_trade_stats = self.UI.user_input(
        #     "show_trade_stats",
        #     enums.UserInputTypes.BOOLEAN,
        #     True,
        #     inputs,
        #     title="Show Trade Stats",
        #     parent_input_name=self.GENERAL_SETTINGS_NAME,
        #     other_schema_values={
        #         "description": "Displays the trade stats for a given configuration. "
        #         "Useful for optimizing the settings in the Feature Engineering section."
        #         " This should NOT replace backtesting and should be used for "
        #         "calibration purposes only. Early Signal Flips represent instances "
        #         "where the model changes signals before 4 bars elapses; high values can"
        #         " indicate choppy (ranging) market conditions."
        #     },
        # )
        # self.use_worst_case_estimates = self.UI.user_input(
        #     "use_worst_case_estimates",
        #     enums.UserInputTypes.BOOLEAN,
        #     False,
        #     inputs,
        #     title="Use Worst Case Estimates",
        #     parent_input_name=self.GENERAL_SETTINGS_NAME,
        #     other_schema_values={
        #         "description": "Whether to use the worst case scenario for backtesting."
        #         " This option can be useful for creating a conservative estimate that "
        #         "is based on close prices only, thus avoiding the effects of intrabar "
        #         "repainting. This option assumes that the user does not enter when the "
        #         "signal first appears and instead waits for the bar to close as "
        #         "confirmation. On larger timeframes, this can mean entering after a "
        #         "large move has already occurred. Leaving this option disabled is "
        #         "generally better for those that use this indicator as a source of "
        #         "confluence and prefer estimates that demonstrate discretionary "
        #         "mid-bar entries. Leaving this option enabled may be more consistent "
        #         "with traditional backtesting results."
        #     },
        # )

    def _init_feature_engineering_settings(self, inputs: dict) -> None:
        # Feature Variables: User-Defined Inputs for calculating Feature Series.
        self.UI.user_input(
            self.FEATURE_ENGINEERING_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Feature Engineering Settings",
        )
        plot_features = self.UI.user_input(
            "plot_features",
            enums.UserInputTypes.BOOLEAN,
            title="Plot Features",
            def_val=False,
            registered_inputs=inputs,
            parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
        )
        feature_count = self.UI.user_input(
            "feature_count",
            enums.UserInputTypes.INT,
            5,
            inputs,
            min_val=2,
            max_val=5,
            title="Feature Count",
            parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
            other_schema_values={
                "description": "Number of features to use for ML predictions."
            },
        )

        feature_1_settings_name = "feature_1_settings"
        self.UI.user_input(
            feature_1_settings_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Feature 1",
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
            },
            parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
        )
        f1_string = self.UI.user_input(
            "f1_string",
            enums.UserInputTypes.OPTIONS,
            title="Feature 1",
            def_val="RSI",
            registered_inputs=inputs,
            options=["RSI", "WT", "CCI", "ADX"],
            other_schema_values={
                "description": "The first feature to use for ML predictions."
            },
            parent_input_name=feature_1_settings_name,
        )
        f1_paramA = self.UI.user_input(
            "f1_paramA",
            enums.UserInputTypes.INT,
            title="Parameter A",
            def_val=14,
            registered_inputs=inputs,
            other_schema_values={"description": "The primary parameter of feature 1."},
            parent_input_name=feature_1_settings_name,
        )
        f1_paramB = self.UI.user_input(
            "f1_paramB",
            enums.UserInputTypes.INT,
            title="Parameter B",
            def_val=1,
            registered_inputs=inputs,
            other_schema_values={
                "description": "The secondary parameter of feature 2 (if applicable)."
            },
            parent_input_name=feature_1_settings_name,
        )
        feature_2_settings_name = "feature_2_settings"
        self.UI.user_input(
            feature_2_settings_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Feature 2",
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
            },
            parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
        )
        f2_string = self.UI.user_input(
            "f2_string",
            enums.UserInputTypes.OPTIONS,
            title="Feature 2",
            def_val="WT",
            registered_inputs=inputs,
            options=["RSI", "WT", "CCI", "ADX"],
            other_schema_values={
                "description": "The second feature to use for ML predictions."
            },
            parent_input_name=feature_2_settings_name,
        )
        f2_paramA = self.UI.user_input(
            "f2_paramA",
            enums.UserInputTypes.INT,
            title="Parameter A",
            def_val=10,
            registered_inputs=inputs,
            other_schema_values={"description": "The primary parameter of feature 2."},
            parent_input_name=feature_2_settings_name,
        )
        f2_paramB = self.UI.user_input(
            "f2_paramB",
            enums.UserInputTypes.INT,
            title="Parameter B",
            def_val=11,
            registered_inputs=inputs,
            other_schema_values={
                "description": "The secondary parameter of feature 2 (if applicable)."
            },
            parent_input_name=feature_2_settings_name,
        )
        f3_string = None
        f3_paramA = None
        f3_paramB = None
        f4_string = None
        f4_paramA = None
        f4_paramB = None
        f5_string = None
        f5_paramA = None
        f5_paramB = None
        if feature_count > 2:
            feature_3_settings_name = "feature_3_settings"
            self.UI.user_input(
                feature_3_settings_name,
                enums.UserInputTypes.OBJECT,
                None,
                inputs,
                title="Feature 3",
                editor_options={
                    matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
                },
                parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
            )
            f3_string = self.UI.user_input(
                "f3_string",
                enums.UserInputTypes.OPTIONS,
                title="Feature 3",
                def_val="CCI",
                registered_inputs=inputs,
                options=["RSI", "WT", "CCI", "ADX"],
                other_schema_values={
                    "description": "The third feature to use for ML predictions."
                },
                parent_input_name=feature_3_settings_name,
            )
            f3_paramA = self.UI.user_input(
                "f3_paramA",
                enums.UserInputTypes.INT,
                title="Parameter A",
                def_val=20,
                registered_inputs=inputs,
                other_schema_values={
                    "description": "The primary parameter of feature 3."
                },
                parent_input_name=feature_3_settings_name,
            )
            f3_paramB = self.UI.user_input(
                "f3_paramB",
                enums.UserInputTypes.INT,
                title="Parameter B",
                def_val=1,
                registered_inputs=inputs,
                other_schema_values={
                    "description": "The secondary parameter of feature "
                    "3 (if applicable)."
                },
                parent_input_name=feature_3_settings_name,
            )
            if feature_count > 3:
                feature_4_settings_name = "feature_4_settings"
                self.UI.user_input(
                    feature_4_settings_name,
                    enums.UserInputTypes.OBJECT,
                    None,
                    inputs,
                    title="Feature 4",
                    editor_options={
                        matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
                    },
                    parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
                )

                f4_string = self.UI.user_input(
                    "f4_string",
                    enums.UserInputTypes.OPTIONS,
                    title="Feature 4",
                    def_val="ADX",
                    registered_inputs=inputs,
                    options=["RSI", "WT", "CCI", "ADX"],
                    other_schema_values={
                        "description": "The fourth feature to use for ML predictions."
                    },
                    parent_input_name=feature_4_settings_name,
                )
                f4_paramA = self.UI.user_input(
                    "f4_paramA",
                    enums.UserInputTypes.INT,
                    title="Parameter A",
                    def_val=20,
                    registered_inputs=inputs,
                    other_schema_values={
                        "description": "The primary parameter of feature 4."
                    },
                    parent_input_name=feature_4_settings_name,
                )
                f4_paramB = self.UI.user_input(
                    "f4_paramB",
                    enums.UserInputTypes.INT,
                    title="Parameter B",
                    def_val=2,
                    registered_inputs=inputs,
                    other_schema_values={
                        "description": "The secondary parameter of feature "
                        "4 (if applicable)."
                    },
                    parent_input_name=feature_4_settings_name,
                )
                if feature_count > 4:
                    feature_5_settings_name = "feature_5_settings"
                    self.UI.user_input(
                        feature_5_settings_name,
                        enums.UserInputTypes.OBJECT,
                        None,
                        inputs,
                        title="Feature 5",
                        editor_options={
                            matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
                        },
                        parent_input_name=self.FEATURE_ENGINEERING_SETTINGS_NAME,
                    )

                    f5_string = self.UI.user_input(
                        "f5_string",
                        enums.UserInputTypes.OPTIONS,
                        title="Feature 5",
                        def_val="RSI",
                        registered_inputs=inputs,
                        options=["RSI", "WT", "CCI", "ADX"],
                        other_schema_values={
                            "description": "The fifth feature to use for "
                            "ML predictions."
                        },
                        parent_input_name=feature_5_settings_name,
                    )
                    f5_paramA = self.UI.user_input(
                        "f5_paramA",
                        enums.UserInputTypes.INT,
                        title="Parameter A",
                        def_val=9,
                        registered_inputs=inputs,
                        other_schema_values={
                            "description": "The primary parameter of feature 5."
                        },
                        parent_input_name=feature_5_settings_name,
                    )
                    f5_paramB = self.UI.user_input(
                        "f5_paramB",
                        enums.UserInputTypes.INT,
                        title="Parameter B",
                        def_val=1,
                        registered_inputs=inputs,
                        other_schema_values={
                            "description": "The secondary parameter of feature "
                            "5 (if applicable)."
                        },
                        parent_input_name=feature_5_settings_name,
                    )
        self.feature_engineering_settings = utils.FeatureEngineeringSettings(
            feature_count=feature_count,
            plot_features=plot_features,
            f1_string=f1_string,
            f1_paramA=f1_paramA,
            f1_paramB=f1_paramB,
            f2_string=f2_string,
            f2_paramA=f2_paramA,
            f2_paramB=f2_paramB,
            f3_string=f3_string,
            f3_paramA=f3_paramA,
            f3_paramB=f3_paramB,
            f4_string=f4_string,
            f4_paramA=f4_paramA,
            f4_paramB=f4_paramB,
            f5_string=f5_string,
            f5_paramA=f5_paramA,
            f5_paramB=f5_paramB,
        )

    def _init_display_settings(self, inputs: dict) -> None:
        self.UI.user_input(
            self.DISPLAY_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Display Settings",
        )
        self.display_settings: utils.DisplaySettings = utils.DisplaySettings(
            show_bar_colors=False,
            # show_bar_colors=self.UI.user_input(
            #     "show_bar_colors",
            #     enums.UserInputTypes.BOOLEAN,
            #     True,
            #     inputs,
            #     title="Show Bar Colors",
            #     parent_input_name=self.DISPLAY_SETTINGS_NAME,
            #     other_schema_values={"description": "Whether to show the bar colors."},
            # ),
            show_bar_predictions=self.UI.user_input(
                "show_bar_predictions",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Show Bar Prediction Values",
                parent_input_name=self.DISPLAY_SETTINGS_NAME,
                other_schema_values={
                    "description": "Will show the ML model's evaluation "
                    "of each bar as an integer."
                },
            ),
            bar_predictions_offset=8,
            # bar_predictions_offset=self.UI.user_input(
            #     "bar_predictions_offset",
            #     enums.UserInputTypes.FLOAT,
            #     8,
            #     inputs,
            #     min_val=0,
            #     max_val=100,
            #     title="Bar Prediction Offset",
            #     parent_input_name=self.DISPLAY_SETTINGS_NAME,
            #     other_schema_values={
            #         "description": "The offset of the bar predictions as a percentage "
            #         "from the bar high or close."
            #     },
            # ),
            use_atr_offset=False,
            # use_atr_offset=self.UI.user_input(
            #     "use_atr_offset",
            #     enums.UserInputTypes.BOOLEAN,
            #     False,
            #     inputs,
            #     title="Use ATR Offset",
            #     parent_input_name=self.DISPLAY_SETTINGS_NAME,
            #     other_schema_values={
            #         "description": "Will use the ATR offset instead of "
            #         "the bar prediction offset."
            #     },
            # ),
            enable_additional_plots=self.UI.user_input(
                "enable_additional_plots",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Enable additional plots",
                parent_input_name=self.DISPLAY_SETTINGS_NAME,
            ),
        )

    def _init_kernel_settings(self, inputs: dict) -> None:
        self.UI.user_input(
            self.KERNEL_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Kernel Settings",
        )
        self.kernel_settings: utils.KernelSettings = utils.KernelSettings(
            use_kernel_filter=self.UI.user_input(
                "use_kernel_filter",
                enums.UserInputTypes.BOOLEAN,
                True,
                inputs,
                title="Trade with Kernel",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
            ),
            show_kernel_estimate=self.UI.user_input(
                "show_kernel_estimate",
                enums.UserInputTypes.BOOLEAN,
                True,
                inputs,
                title="Show Kernel Estimate",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
            ),
            use_kernel_smoothing=self.UI.user_input(
                "use_kernel_smoothing",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Enhance Kernel Smoothing",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
                other_schema_values={
                    "description": "Uses a crossover based mechanism "
                    "to smoothen kernel color changes. This often "
                    "results in less color transitions overall and "
                    "may result in more ML entry signals being generated."
                },
            ),
            lookback_window=self.UI.user_input(
                "lookback_window",
                enums.UserInputTypes.INT,
                8,
                inputs,
                min_val=0,
                max_val=100,
                title="Lookback Window",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
                other_schema_values={
                    "description": "The number of bars used for the estimation. This is"
                    " a sliding value that represents the most recent historical bars. "
                    "Recommended range: 3-50"
                },
            ),
            relative_weighting=self.UI.user_input(
                "relative_weighting",
                enums.UserInputTypes.FLOAT,
                8,
                inputs,
                min_val=0,
                max_val=100,
                title="Relative Weighting",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
                other_schema_values={
                    "description": "Relative weighting of time frames. As this value "
                    "approaches zero, the longer time frames will exert more influence "
                    "on the estimation. As this value approaches infinity, the behavior"
                    " of the Rational Quadratic Kernel will become identical to the "
                    "Gaussian kernel. Recommended range: 0.25-25"
                },
            ),
            regression_level=self.UI.user_input(
                "regression_level",
                enums.UserInputTypes.INT,
                25,
                inputs,
                min_val=0,
                max_val=100,
                title="Regression Level",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
                other_schema_values={
                    "description": "Bar index on which to start regression. Controls "
                    "how tightly fit the kernel estimate is to the data. Smaller values"
                    " are a tighter fit. Larger values are a looser fit. Recommended "
                    "range: 2-25"
                },
            ),
            lag=self.UI.user_input(
                "lag",
                enums.UserInputTypes.INT,
                2,
                inputs,
                min_val=0,
                max_val=100,
                title="Lag",
                parent_input_name=self.KERNEL_SETTINGS_NAME,
                other_schema_values={
                    "description": "Lag for crossover detection. Lower values result in"
                    " earlier crossovers. Recommended range: 1-2"
                },
            ),
        )

    def _init_order_settings(self, inputs: dict) -> None:
        self.UI.user_input(
            self.ORDER_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Order Settings",
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
            },
        )
        leverage: int = None
        if self.exchange_manager.is_future:
            leverage = self.UI.user_input(
                "leverage",
                enums.UserInputTypes.INT,
                1,
                inputs,
                min_val=1,
                max_val=125,
                title="Leverage",
                parent_input_name=self.ORDER_SETTINGS_NAME,
                editor_options={
                    matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
                },
                other_schema_values={
                    matrix_enums.UserInputOtherSchemaValuesTypes.DESCRIPTION.value: "Leverage"
                    " to use for futures trades"
                },
            )
        long_order_volume: float = None
        enable_long_orders: bool = self.UI.user_input(
            "enable_long_orders",
            enums.UserInputTypes.BOOLEAN,
            True,
            inputs,
            title="Enable long tading",
            parent_input_name=self.ORDER_SETTINGS_NAME,
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        if enable_long_orders:
            long_order_volume = self.UI.user_input(
                "long_order_volume",
                enums.UserInputTypes.FLOAT,
                50,
                inputs,
                min_val=0.1,
                max_val=100,
                title="% of available balance to use for long trades",
                parent_input_name=self.ORDER_SETTINGS_NAME,
                editor_options={
                    matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
                },
            )
        enable_short_orders: bool = False
        short_order_volume: float = None
        if self.exchange_manager.is_future:
            enable_short_orders = self.UI.user_input(
                "enable_short_orders",
                enums.UserInputTypes.BOOLEAN,
                True,
                inputs,
                title="Enable short tading",
                parent_input_name=self.ORDER_SETTINGS_NAME,
                editor_options={
                    matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
                },
            )
            if enable_short_orders:
                short_order_volume = self.UI.user_input(
                    "short_order_volume",
                    enums.UserInputTypes.FLOAT,
                    50,
                    inputs,
                    min_val=0.1,
                    max_val=100,
                    title="% of available balance to use for short trades",
                    parent_input_name=self.ORDER_SETTINGS_NAME,
                    editor_options={
                        matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
                    },
                )
        self.order_settings: utils.LorentzianOrderSettings = (
            utils.LorentzianOrderSettings(
                enable_short_orders=enable_short_orders,
                short_order_volume=short_order_volume,
                long_order_volume=long_order_volume,
                enable_long_orders=enable_long_orders,
                leverage=leverage,
            )
        )

    def _init_filter_settings(self, inputs: dict) -> None:
        self.UI.user_input(
            self.FILTER_SETTINGS_NAME,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Filter Settings",
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 12
            },
        )
        volatility_filter_name = "volatility_filter_settings"
        self.UI.user_input(
            volatility_filter_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Volatility Filter Settings",
            parent_input_name=self.FILTER_SETTINGS_NAME,
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        use_volatility_filter = self.UI.user_input(
            "use_volatility_filter",
            enums.UserInputTypes.BOOLEAN,
            True,
            inputs,
            title="Use Volatility Filter",
            parent_input_name=volatility_filter_name,
            other_schema_values={
                "description": "Whether to use the volatility filter.",
            },
        )
        plot_volatility_filter = False
        if use_volatility_filter:
            plot_volatility_filter = self.UI.user_input(
                "plot_volatility_filter",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Plot Volatility Filter",
                parent_input_name=volatility_filter_name,
            )

        regime_filter_name = "regime_filter_settings"
        self.UI.user_input(
            regime_filter_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="Regime Filter Settings",
            parent_input_name=self.FILTER_SETTINGS_NAME,
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        use_regime_filter = self.UI.user_input(
            "use_regime_filter",
            enums.UserInputTypes.BOOLEAN,
            True,
            inputs,
            title="Use Regime Filter",
            parent_input_name=regime_filter_name,
        )
        plot_regime_filter = False
        regime_threshold = None
        if use_regime_filter:
            plot_regime_filter = self.UI.user_input(
                "plot_regime_filter",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Plot Regime Filter",
                parent_input_name=regime_filter_name,
            )
            regime_threshold = self.UI.user_input(
                "regime_threshold",
                enums.UserInputTypes.FLOAT,
                -0.1,
                inputs,
                min_val=-10,
                max_val=10,
                title="Regime Threshold",
                parent_input_name=regime_filter_name,
                other_schema_values={
                    "description": "Whether to use the trend detection filter. "
                    "Threshold for detecting Trending/Ranging markets. Use steps of 0.1"
                },
            )

        adx_filter_name = "adx_filter_settings"
        self.UI.user_input(
            adx_filter_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="ADX Filter Settings",
            parent_input_name=self.FILTER_SETTINGS_NAME,
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        use_adx_filter = self.UI.user_input(
            "use_adx_filter",
            enums.UserInputTypes.BOOLEAN,
            False,
            inputs,
            title="Use ADX Filter",
            parent_input_name=adx_filter_name,
        )
        plot_adx_filter = False
        adx_threshold = None
        if use_adx_filter:
            plot_adx_filter = self.UI.user_input(
                "plot_adx_filter",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Plot EMA Filter",
                parent_input_name=adx_filter_name,
            )
            adx_threshold = self.UI.user_input(
                "adx_threshold",
                enums.UserInputTypes.INT,
                20,
                inputs,
                min_val=0,
                max_val=100,
                title="ADX Threshold",
                parent_input_name=adx_filter_name,
                other_schema_values={
                    "description": "Whether to use the ADX filter. "
                    "Threshold for detecting Trending/Ranging markets."
                },
            )
        ema_filter_name = "ema_filter_settings"
        self.UI.user_input(
            ema_filter_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="EMA Filter Settings",
            parent_input_name=self.FILTER_SETTINGS_NAME,
            editor_options={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        use_ema_filter = self.UI.user_input(
            "use_ema_filter",
            enums.UserInputTypes.BOOLEAN,
            False,
            inputs,
            title="Use EMA Filter",
            parent_input_name=ema_filter_name,
        )
        plot_ema_filter = False
        ema_period = None
        if use_ema_filter:
            plot_ema_filter = self.UI.user_input(
                "plot_ema_filter",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Plot EMA Filter",
                parent_input_name=ema_filter_name,
            )

            ema_period = self.UI.user_input(
                "ema_period",
                enums.UserInputTypes.INT,
                200,
                inputs,
                min_val=1,
                title="EMA Period",
                parent_input_name=ema_filter_name,
                other_schema_values={
                    "description": "The period of the EMA used for the EMA Filter."
                },
            )
        sma_filter_name = "sma_filter_settings"
        self.UI.user_input(
            sma_filter_name,
            enums.UserInputTypes.OBJECT,
            None,
            inputs,
            title="SMA Filter Settings",
            parent_input_name=self.FILTER_SETTINGS_NAME,
            other_schema_values={
                matrix_enums.UserInputEditorOptionsTypes.GRID_COLUMNS.value: 6
            },
        )
        use_sma_filter = self.UI.user_input(
            "use_sma_filter",
            enums.UserInputTypes.BOOLEAN,
            False,
            inputs,
            title="Use SMA Filter",
            parent_input_name=sma_filter_name,
        )
        plot_sma_filter = False
        sma_period = None
        if use_sma_filter:
            plot_sma_filter = self.UI.user_input(
                "plot_sma_filter",
                enums.UserInputTypes.BOOLEAN,
                False,
                inputs,
                title="Plot SMA Filter",
                parent_input_name=sma_filter_name,
            )
            sma_period = self.UI.user_input(
                "sma_period",
                enums.UserInputTypes.INT,
                200,
                inputs,
                min_val=1,
                title="SMA Period",
                parent_input_name=sma_filter_name,
                other_schema_values={
                    "description": "The period of the SMA used for the SMA Filter."
                },
            )

        self.filter_settings: utils.FilterSettings = utils.FilterSettings(
            use_volatility_filter=use_volatility_filter,
            plot_volatility_filter=plot_volatility_filter,
            use_regime_filter=use_regime_filter,
            regime_threshold=regime_threshold,
            plot_regime_filter=plot_regime_filter,
            use_adx_filter=use_adx_filter,
            adx_threshold=adx_threshold,
            plot_adx_filter=plot_adx_filter,
            use_ema_filter=use_ema_filter,
            ema_period=ema_period,
            plot_ema_filter=plot_ema_filter,
            use_sma_filter=use_sma_filter,
            sma_period=sma_period,
            plot_sma_filter=plot_sma_filter,
        )
