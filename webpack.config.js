const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => ({
    entry: [
        './askomics/react/src/index.jsx'
    ],
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    output: {
        path: __dirname + '/askomics/static/js',
        filename: 'askomics.js'
    },
    resolve: {
        extensions: ['.js', '.jsx'],
    },
    optimization: {
      minimize: (argv.mode === 'production') ? true : false,
      minimizer: [new TerserPlugin()],
    },
});

// module.exports = config;
