module.exports = {
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
                use: ["css-loader"]
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
