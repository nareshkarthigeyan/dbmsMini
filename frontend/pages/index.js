import Link from 'next/link'

export default function Home(){
  return (
    <div>
      <h1>Multi-Service Platform — Frontend</h1>
      <p>Choose an entity to manage:</p>
      <ul>
        <li><Link href="/users">Users</Link></li>
        <li><Link href="/drivers">Drivers</Link></li>
        <li><Link href="/restaurants">Restaurants</Link></li>
        <li><Link href="/menu-items">Menu Items</Link></li>
        <li><Link href="/orders">Orders</Link></li>
        <li><Link href="/rides">Rides</Link></li>
        <li><Link href="/payments">Payments</Link></li>
        <li><Link href="/ratings">Ratings</Link></li>
      </ul>
    </div>
  )
}
