using UnityEngine;

namespace SF3.NeonSiege
{
    public static class SiegeBallistics
    {
        public const float Radius = 0.14f;
        public const float Gravity = -9.81f;
        public const float StepTime = 0.02f;
        public const float MinSpeed = 9;
        public const float MaxSpeed = 18;

        public static bool AimAt(Vector2 origin, Vector2 target, float speed, bool highArc, out Vector2 velocity)
        {
            velocity = Vector2.zero;
            if (target.x <= origin.x + 0.15f) return false;
            bool found = false;
            float previousTime = 0.08f;
            float previous = RequiredVelocity(origin, target, previousTime).sqrMagnitude - speed * speed;
            for (int i = 5; i <= 180; i++)
            {
                float time = i * StepTime;
                float current = RequiredVelocity(origin, target, time).sqrMagnitude - speed * speed;
                if (previous * current <= 0)
                {
                    float left = previousTime, right = time;
                    for (int j = 0; j < 14; j++)
                    {
                        float mid = (left + right) * 0.5f;
                        float test = RequiredVelocity(origin, target, mid).sqrMagnitude - speed * speed;
                        if (test * previous > 0) left = mid; else right = mid;
                    }
                    Vector2 candidate = RequiredVelocity(origin, target, (left + right) * 0.5f);
                    float angle = Mathf.Atan2(candidate.y, candidate.x) * Mathf.Rad2Deg;
                    if (angle >= 8 && angle <= 78)
                    {
                        velocity = candidate; found = true;
                        if (!highArc) return true;
                    }
                }
                previous = current; previousTime = time;
            }
            return found;
        }

        private static Vector2 RequiredVelocity(Vector2 origin, Vector2 target, float time)
        {
            Vector2 result = (target - origin) / time;
            result.y -= 0.5f * Gravity * (time + StepTime);
            return result;
        }

        // Same semi-implicit Euler integration used by an undamped Rigidbody2D.
        public static void Step(ref Vector2 position, ref Vector2 velocity, float step)
        {
            velocity.y += Gravity * step;
            position += velocity * step;
        }

        public static Vector2 Position(Vector2 origin, Vector2 velocity, float time)
        {
            int count = Mathf.FloorToInt(time / StepTime);
            for (int i = 0; i < count; i++) Step(ref origin, ref velocity, StepTime);
            if (time - count * StepTime > 0.0001f) Step(ref origin, ref velocity, time - count * StepTime);
            return origin;
        }

        public static Vector2 Velocity(float angle, float speed)
            => new Vector2(Mathf.Cos(angle * Mathf.Deg2Rad), Mathf.Sin(angle * Mathf.Deg2Rad)) * speed;

        public static bool SegmentCircle(Vector2 from, Vector2 to, Vector2 center, float radius)
        {
            Vector2 line = to - from;
            float u = line.sqrMagnitude < 0.000001f ? 0 : Mathf.Clamp01(Vector2.Dot(center - from, line) / line.sqrMagnitude);
            return (from + line * u - center).sqrMagnitude <= radius * radius;
        }

        public static bool Solve(Vector2 origin, Vector2 destination, float time, out Vector2 velocity)
        {
            int count = Mathf.Max(1, Mathf.RoundToInt(time / StepTime));
            time = count * StepTime;
            velocity = (destination - origin) / time;
            velocity.y -= Gravity * StepTime * (count + 1) * 0.5f;
            float angle = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
            return velocity.magnitude >= MinSpeed && velocity.magnitude <= MaxSpeed && angle >= 8 && angle <= 78;
        }
    }
}
