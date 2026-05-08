<?php

declare(strict_types=1);

/**
 * NOTICE OF LICENSE.
 *
 * UNIT3D Community Edition is open-sourced software licensed under the GNU Affero General Public License v3.0
 * The details is bundled with this project in the file LICENSE.txt.
 *
 * @project    UNIT3D Community Edition
 *
 * @author     HDVinnie <hdinnovations@protonmail.com>
 * @license    https://www.gnu.org/licenses/agpl-3.0.en.html/ GNU Affero General Public License v3.0
 */

namespace App\Providers;

use App\Enums\GlobalRateLimit;
use App\Enums\MiddlewareGroup;
use Illuminate\Auth\Middleware\RedirectIfAuthenticated;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Foundation\Support\Providers\RouteServiceProvider as ServiceProvider;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;

class RouteServiceProvider extends ServiceProvider
{
    /**
     * The path to the "home" route for your application.
     *
     * This is used by Laravel authentication to redirect users after login.
     *
     * @var string
     */
    final public const HOME = '/';

    /**
     * Define your route model bindings, pattern filters, etc.
     */
    public function boot(): void
    {
        $this->configureRateLimiting();

        $this->removeIndexPhpFromUrl();

        $this->routes(function (): void {
            Route::prefix('api')
                ->middleware(MiddlewareGroup::CHAT->value)
                ->group(base_path('routes/vue.php'));

            Route::middleware(MiddlewareGroup::WEB->value)
                ->group(base_path('routes/web.php'));

            Route::prefix('api')
                ->middleware(MiddlewareGroup::API->value)
                ->group(base_path('routes/api.php'));

            Route::prefix('announce')
                ->middleware(MiddlewareGroup::ANNOUNCE->value)
                ->group(base_path('routes/announce.php'));

            Route::middleware(MiddlewareGroup::RSS->value)
                ->group(base_path('routes/rss.php'));
        });

        RedirectIfAuthenticated::redirectUsing(fn () => self::HOME);
    }

    /**
     * Configure the rate limiters for the application.
     */
    protected function configureRateLimiting(): void
    {
        RateLimiter::for(GlobalRateLimit::WEB, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::API, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::ANNOUNCE, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::CHAT, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::RSS, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::AUTHENTICATED_IMAGES, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::SEARCH, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::TMDB, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::IGDB, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::FORGOT_PASSWORD, fn () => Limit::none());
        RateLimiter::for(GlobalRateLimit::RESET_PASSWORD, fn () => Limit::none());
    }

    protected function removeIndexPhpFromUrl(): void
    {
        if (str_contains(request()->getRequestUri(), '/index.php/')) {
            $url = str_replace('index.php/', '', request()->getRequestUri());

            if ($url !== '') {
                header("Location: {$url}", true, 301);

                exit;
            }
        }
    }
}
