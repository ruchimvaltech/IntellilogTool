namespace SupportDashboard.Models
{
    public class Ticket
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Urgency { get; set; }
        public string Status { get; set; }
    }
}
