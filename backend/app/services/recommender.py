"""Recommendation service with ML-backed strategies."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import List

import numpy as np
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.interaction import UserProductInteraction
from app.models.product import Product
from app.schemas.recommendation import ProductRecommendation, RecommendationResponse

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.models.collaborative_filtering import CollaborativeFilteringModel
from ml.models.content_based import ContentBasedModel
from ml.models.hybrid import HybridRecommender


class RecommenderService:
    """Service for generating recommendations using multiple strategies."""

    def __init__(self):
        self.hybrid_model = HybridRecommender()
        self.content_model: ContentBasedModel | None = None
        self.collaborative_model: CollaborativeFilteringModel | None = None
        self._product_count: int | None = None
        self._interaction_count: int | None = None

    def _fetch_products(self, db: Session) -> list[Product]:
        return db.query(Product).all()

    def _product_payloads(self, products: list[Product]) -> list[dict]:
        payloads: list[dict] = []
        for product in products:
            payloads.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "description": product.description,
                    "category": product.category,
                    "category_raw": product.category_raw,
                    "tags": product.tags or [],
                    "average_rating": product.average_rating or 0.0,
                    "review_count": product.review_count or 0,
                }
            )
        return payloads

    def _ensure_models(self, db: Session):
        product_count = db.query(func.count(Product.id)).scalar() or 0
        interaction_count = db.query(func.count(UserProductInteraction.id)).scalar() or 0

        if (
            self.content_model is not None
            and self._product_count == product_count
            and self._interaction_count == interaction_count
        ):
            return

        products = self._fetch_products(db)
        product_payloads = self._product_payloads(products)

        self.content_model = ContentBasedModel()
        if product_payloads:
            self.content_model.fit(product_payloads)

        self.collaborative_model = None
        if interaction_count:
            product_ids = [product.id for product in products]
            user_ids = [
                user_id
                for (user_id,) in db.query(UserProductInteraction.user_id)
                .distinct()
                .order_by(UserProductInteraction.user_id)
                .all()
            ]
            if user_ids and product_ids:
                user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
                product_index = {product_id: idx for idx, product_id in enumerate(product_ids)}
                interaction_matrix = np.zeros((len(user_ids), len(product_ids)), dtype=float)

                interactions = (
                    db.query(
                        UserProductInteraction.user_id,
                        UserProductInteraction.product_id,
                        UserProductInteraction.interaction_weight,
                    )
                    .all()
                )
                for user_id, product_id, interaction_weight in interactions:
                    row = user_index.get(user_id)
                    col = product_index.get(product_id)
                    if row is None or col is None:
                        continue
                    interaction_matrix[row, col] += float(interaction_weight or 0.0)

                self.collaborative_model = CollaborativeFilteringModel()
                self.collaborative_model.fit(
                    interaction_matrix=interaction_matrix,
                    user_ids=user_ids,
                    item_ids=product_ids,
                )

        self._product_count = product_count
        self._interaction_count = interaction_count

    def _popular_recommendations(self, db: Session, limit: int) -> list[ProductRecommendation]:
        top_products = (
            db.query(Product)
            .order_by(desc(Product.review_count), desc(Product.average_rating), Product.id.asc())
            .limit(limit)
            .all()
        )
        return [
            ProductRecommendation(
                product_id=product.id,
                score=float((product.review_count or 0) + (product.average_rating or 0.0)),
                reason="Popular with strong review activity",
            )
            for product in top_products
        ]

    def _popular_pairs(
        self,
        db: Session,
        limit: int,
        exclude_product_ids: set[int] | None = None,
    ) -> list[tuple[int, float]]:
        exclude_product_ids = exclude_product_ids or set()
        products = (
            db.query(Product)
            .order_by(desc(Product.review_count), desc(Product.average_rating), Product.id.asc())
            .limit(limit * 3)
            .all()
        )
        pairs: list[tuple[int, float]] = []
        for product in products:
            if product.id in exclude_product_ids:
                continue
            pairs.append(
                (
                    product.id,
                    float((product.review_count or 0) + (product.average_rating or 0.0)),
                )
            )
            if len(pairs) >= limit:
                break
        return pairs

    def _recommendations_from_pairs(
        self,
        pairs: list[tuple[int, float]],
        reason: str,
        limit: int,
    ) -> list[ProductRecommendation]:
        return [
            ProductRecommendation(product_id=product_id, score=float(score), reason=reason)
            for product_id, score in pairs[:limit]
        ]

    def _rerank_with_diversity(
        self,
        db: Session,
        pairs: list[tuple[int, float]],
        limit: int,
        reason: str,
    ) -> list[ProductRecommendation]:
        """Balance raw relevance with light category/brand diversity."""
        if not pairs:
            return []

        product_ids = [product_id for product_id, _ in pairs]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        product_map = {product.id: product for product in products}

        remaining = list(pairs)
        chosen: list[tuple[int, float]] = []
        used_categories: dict[str, int] = {}
        used_brands: dict[str, int] = {}

        while remaining and len(chosen) < limit:
            best_index = 0
            best_score = None
            for idx, (product_id, base_score) in enumerate(remaining):
                product = product_map.get(product_id)
                category_key = (product.category if product else "") or ""
                brand_key = (product.brand if product else "") or ""
                category_penalty = 0.12 * used_categories.get(category_key, 0)
                brand_penalty = 0.06 * used_brands.get(brand_key, 0)
                review_boost = 0.0
                if product is not None:
                    review_boost = min((product.review_count or 0) / 50000.0, 0.2)
                adjusted_score = float(base_score) + review_boost - category_penalty - brand_penalty
                if best_score is None or adjusted_score > best_score:
                    best_score = adjusted_score
                    best_index = idx

            product_id, base_score = remaining.pop(best_index)
            product = product_map.get(product_id)
            if product is not None:
                used_categories[product.category or ""] = used_categories.get(product.category or "", 0) + 1
                used_brands[product.brand or ""] = used_brands.get(product.brand or "", 0) + 1
            chosen.append((product_id, base_score))

        return self._recommendations_from_pairs(chosen, reason=reason, limit=limit)

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        strategy: str = "hybrid",
        db: Session = None,
    ) -> RecommendationResponse:
        """Get personalized recommendations for a user."""
        if strategy == "collaborative":
            recommendations = await self._collaborative_filtering(user_id, limit, db)
        elif strategy == "content":
            recommendations = await self._content_based_filtering(user_id, limit, db)
        else:
            recommendations = await self._hybrid_recommendations(user_id, limit, db)

        return RecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
            strategy=strategy,
            total_recommendations=len(recommendations),
        )

    async def _collaborative_filtering(
        self, user_id: int, limit: int, db: Session
    ) -> List[ProductRecommendation]:
        """Collaborative filtering approach."""
        self._ensure_models(db)

        user_interactions = (
            db.query(UserProductInteraction)
            .filter(UserProductInteraction.user_id == user_id)
            .all()
        )
        interacted_ids = [interaction.product_id for interaction in user_interactions]

        if not user_interactions or self.collaborative_model is None:
            return self._popular_recommendations(db, limit)

        predictions = self.collaborative_model.predict(
            user_id=user_id,
            top_k=limit,
            exclude_item_ids=interacted_ids,
        )
        if not predictions:
            return self._popular_recommendations(db, limit)

        return self._rerank_with_diversity(
            db,
            predictions,
            reason="Based on patterns from similar shoppers",
            limit=limit,
        )

    async def _content_based_filtering(
        self, user_id: int, limit: int, db: Session
    ) -> List[ProductRecommendation]:
        """Content-based filtering approach."""
        self._ensure_models(db)

        user_interactions = (
            db.query(UserProductInteraction)
            .filter(UserProductInteraction.user_id == user_id)
            .order_by(UserProductInteraction.timestamp.desc())
            .all()
        )
        interacted_ids = [interaction.product_id for interaction in user_interactions]

        if self.content_model is None:
            return self._popular_recommendations(db, limit)

        if not interacted_ids:
            top_products = (
                db.query(Product)
                .order_by(desc(Product.average_rating), desc(Product.review_count))
                .limit(limit)
                .all()
            )
            return [
                ProductRecommendation(
                    product_id=product.id,
                    score=float(product.average_rating or 0.0),
                    reason="Strong match from product content signals",
                )
                for product in top_products
            ]

        predictions = self.content_model.recommend_from_history(
            seed_product_ids=interacted_ids,
            top_k=limit,
            exclude_product_ids=interacted_ids,
        )
        if not predictions:
            return self._popular_recommendations(db, limit)

        return self._rerank_with_diversity(
            db,
            predictions,
            reason="Based on product content similar to your activity",
            limit=limit,
        )

    async def _hybrid_recommendations(
        self, user_id: int, limit: int, db: Session
    ) -> List[ProductRecommendation]:
        """Hybrid approach combining collaborative and content-based strategies."""
        self._ensure_models(db)

        user_interactions = (
            db.query(UserProductInteraction)
            .filter(UserProductInteraction.user_id == user_id)
            .all()
        )
        interacted_ids = [interaction.product_id for interaction in user_interactions]
        interacted_set = set(interacted_ids)

        if not interacted_ids:
            return self._popular_recommendations(db, limit)

        collaborative_pairs = []
        if self.collaborative_model is not None:
            collaborative_pairs = self.collaborative_model.predict(
                user_id=user_id,
                top_k=limit * 2,
                exclude_item_ids=interacted_ids,
            )
        content_pairs = []
        if self.content_model is not None:
            content_pairs = self.content_model.recommend_from_history(
                seed_product_ids=interacted_ids,
                top_k=limit * 2,
                exclude_product_ids=interacted_ids,
            )
        popular_pairs = self._popular_pairs(db, limit=max(limit * 2, 10), exclude_product_ids=interacted_set)

        if collaborative_pairs and content_pairs:
            hybrid_pairs = self.hybrid_model.recommend(
                cf_predictions=collaborative_pairs,
                cb_predictions=content_pairs,
                top_k=limit * 2,
            )
            blended = {product_id: score for product_id, score in hybrid_pairs}
            for product_id, score in popular_pairs:
                blended[product_id] = blended.get(product_id, 0.0) + (score / 50000.0) * 0.15
            blended_pairs = sorted(blended.items(), key=lambda item: item[1], reverse=True)[: limit * 3]
            return self._rerank_with_diversity(
                db,
                blended_pairs,
                reason="Hybrid ranking from user behavior and product similarity",
                limit=limit,
            )
        if content_pairs:
            return self._rerank_with_diversity(
                db,
                content_pairs,
                reason="Content-based match from your interaction history",
                limit=limit,
            )
        if collaborative_pairs:
            return self._rerank_with_diversity(
                db,
                collaborative_pairs,
                reason="Collaborative match from similar users",
                limit=limit,
            )
        return self._popular_recommendations(db, limit)

    async def _trending_fallback(self, limit: int, db: Session) -> List[ProductRecommendation]:
        """Fallback to trending products when no interaction data exists."""
        trending = await self.get_trending_products(limit, db)
        return trending.recommendations

    async def get_similar_products(
        self, product_id: int, limit: int, db: Session
    ) -> RecommendationResponse:
        """Get products similar to a given product."""
        self._ensure_models(db)

        if self.content_model is not None:
            predictions = self.content_model.get_similar_products(product_id=product_id, top_k=limit)
            if predictions:
                return RecommendationResponse(
                    recommendations=self._rerank_with_diversity(
                        db,
                        predictions,
                        reason="Content similarity from title, brand, description, and tags",
                        limit=limit,
                    ),
                    strategy="content",
                    total_recommendations=min(len(predictions), limit),
                )

        ref_product = db.query(Product).filter(Product.id == product_id).first()
        if not ref_product:
            return RecommendationResponse(recommendations=[], strategy="content", total_recommendations=0)

        similar_products = (
            db.query(Product)
            .filter(Product.category == ref_product.category, Product.id != product_id)
            .order_by(desc(Product.average_rating), desc(Product.review_count))
            .limit(limit)
            .all()
        )
        recommendations = [
            ProductRecommendation(
                product_id=product.id,
                score=float(product.average_rating or 0.0),
                reason="Similar product in the same category",
            )
            for product in similar_products
        ]
        return RecommendationResponse(
            recommendations=recommendations,
            strategy="content",
            total_recommendations=len(recommendations),
        )

    async def get_trending_products(
        self, limit: int, db: Session
    ) -> RecommendationResponse:
        """Get trending products based on recent interactions."""
        one_week_ago = datetime.now() - timedelta(days=7)

        trending_products = (
            db.query(
                Product.id,
                func.count(UserProductInteraction.id).label("interaction_count"),
            )
            .join(UserProductInteraction, Product.id == UserProductInteraction.product_id)
            .filter(UserProductInteraction.timestamp >= one_week_ago)
            .group_by(Product.id)
            .order_by(desc("interaction_count"))
            .limit(limit)
            .all()
        )

        if not trending_products:
            recommendations = self._popular_recommendations(db, limit)
            return RecommendationResponse(
                recommendations=recommendations,
                strategy="trending",
                total_recommendations=len(recommendations),
            )

        recommendations = [
            ProductRecommendation(
                product_id=product_id,
                score=float(count),
                reason="Trending this week",
            )
            for product_id, count in trending_products
        ]
        return RecommendationResponse(
            recommendations=recommendations,
            strategy="trending",
            total_recommendations=len(recommendations),
        )
