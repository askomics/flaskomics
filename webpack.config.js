let config = {
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
                loader: ['style-loader', 'css-loader']
            }
        ]
    },
    output: {
        path: __dirname + '/askomics/static/js',
        filename: 'askomics.js'
    },
    resolve: {
        extensions: ['.js', '.jsx'],
    }
};

module.exports = config;
