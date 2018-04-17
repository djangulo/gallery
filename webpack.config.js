const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

const extractSass = new ExtractTextPlugin({
    filename: 'css/[name].css',
    disable: process.env.NODE_ENV === 'development'
})

module.exports = {
    // watch: true,
    // watchOptions: {
    //     poll: 1000
    // },
    entry: {
        layout: './static/js/layout.js',
        // home django app files
        home: './home/static/home/home.js',
        // photoblog django app files
        photoblog: './photoblog/static/photoblog/photoblog.js',
    },
    output: {
        filename: 'js/[name].bundle.js',
        path: path.resolve(__dirname, 'assets'),
        publicPath: '/'
    },
    module: {
        rules: [{
            test: /\.scss$/,
            use: extractSass.extract({
                use: [
                    {
                        loader: "css-loader",
                        options: {
                            sourceMap: true
                        }
                    }, {
                        loader: "sass-loader"
                    }],
                    fallback: "style-loader"
                }),
        },
        {
            test: /\.(png|svg|jpe?g|gif)$/,
            use: [{
                loader: 'file-loader',
                options: {
                    name: '[name].[hash].[ext]',
                    outputPath: 'images/',
                    publicPath: '/assets/images/'
                }
            }]
        }
    ]
    },
    plugins: [
        extractSass,
        new CleanWebpackPlugin(['assets']),
        // new HtmlWebpackPlugin({
        //     filename:  path.resolve(__dirname, 'templates/layout.bundle.html'),
        //     title: 'JED Art Studio',
        //     chunks: ['layout'],
        //     template: 'templates/layout.html',
        //     inject: false
        // }),
        new HtmlWebpackPlugin({
            filename:  path.resolve(__dirname, 'home/templates/home/home.bundle.html'),
            title: 'Linekode | Home',
            chunks: ['home'],
            template: 'home/templates/home/home.html',
            inject: false
        })
    ]
};
