var gulp = require('gulp');
var less = require('gulp-less');
var cleanCSS = require('gulp-clean-css');
var del = require('del');
var rename = require("gulp-rename");
var watch = require("gulp-watch");

gulp.task('default', function() {
    gulp.src(['less/app.less'])
        .pipe(less())
        .pipe(cleanCSS())
        .pipe(gulp.dest('static/css'));
    gulp.src(['less/tickets.less'])
        .pipe(less())
        .pipe(cleanCSS())
        .pipe(gulp.dest('static/css'))
});

gulp.task('dev', function() {
    gulp.src(['less/app.less'])
        .pipe(less())
        .pipe(gulp.dest('static/css'));
    gulp.src(['less/tickets.less'])
        .pipe(less())
        .pipe(gulp.dest('static/css'))
});

gulp.task('stream', function () {
    // Endless stream mode
    gulp.watch(['less/*.less'], ['dev']);
});
